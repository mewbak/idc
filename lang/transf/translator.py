"""Translates the transformation describing aterms into the 
respective transformation objects."""


# pylint: disable-msg=R0201


import antlr
import aterm.factory
import transf
import walker


class SemanticException(antlr.SemanticException):

	def __init__(self, node, msg):
		antlr.SemanticException.__init__(self)
		self.node = node
		self.msg = msg
	   
	def __str__(self):
		line = self.node.getLine()
		col  = self.node.getColumn()
		text = self.node.getText()
		return "line %s:%s: \"%s\": %s" % (line, col, text, self.msg)

	__repr__ = __str__

SemanticException = Exception


class Meta:
	"""A parsed transformation factory."""

	def __init__(self, globals, locals, args, term):
		self.globals = globals
		self.locals = locals
		self.args = args
		self.term = term
	
	def __call__(self, *args):
		if len(args) != len(self.args):
			raise TypeError("%d arguments required (%d given)" % (len(self.args), len(args)))
		translator = Translator(
			globals = self.globals,
			locals = self.locals,
		)
		translator.stack.append(dict(zip(self.args, args)))
		return translator.transf(self.term)


class Translator(walker.Walker):
	
	def __init__(self, **kwargs):
		self.globals = kwargs.get("globals", {})
		self.locals = kwargs.get("locals", {})
		self.stack = []


	def bind_name(self, name):
		# lookup in the symbol stack
		for i in range(len(self.stack) - 1, -1, -1):
			try:
				return self.stack[i][name]
			except KeyError:
				pass
		
		# lookup in the caller namespace
		try:
			return eval(name, self.globals, self.locals)
		except NameError:
			pass
	
		# lookup in the builtins module
		from lang.transf import builtins
		try:
			return getattr(builtins, name)
		except AttributeError:
			pass

		# lookup in the transf module
		try:
			return eval(name, transf.__dict__)
		except NameError:
			pass
		except AttributeError:
			pass
		
		return None
	
	def define_name(self, name, value):
		# define transf in the local namespace
		eval(compile(name + " = _", "", "single"), {"_": value}, self.locals)

	def translate(self, t):
		return self._dispatch(t, 'translate')
	
	transf_defs = translate
	meta_def = translate
	
	def translateDefs(self, tdefs):
		for tdef in tdefs:
			self.translate(tdef)
	
	def translateTransfDef(self, n, t):
		n = self.id(n)
		t = self.transf(t)
		self.define_name(n, t)

	def translateTransfFacDef(self, n, a, t):
		n = self.id(n)
		T = self.meta(a, t)
		self.define_name(n, T)
	
	def translateMetaDef(self, a, t):
		return self.meta(a, t)


	def meta(self, a, t):
		a = map(self.id, a)
		return Meta(
			self.globals,
			self.locals,
			a,
			t,
		)

	
	def transf(self, t):
		return self._dispatch(t, 'transf')
	
	def transfIdent(self):
		return transf.base.ident
		
	def transfFail(self):
		return transf.base.fail

	def transfMatch(self, t):
		return self.match(t)
		
	def transfBuild(self, t):
		return self.build(t)
		
	def transfTraverse(self, t):
		return self.traverse(t)
		
	def transfSet(self, v):
		v = self.id(v)
		return transf.variable.Set(v)

	def transfUnset(self, v):
		v = self.id(v)
		return transf.variable.Unset(v)
		
	def transfComposition(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return transf.combine.Composition(l, r)
		
	def transfChoice(self, o):
		o = map(self.transf, o)
		return transf.combine.UndeterministicChoice(o)
		
	def transfLeftChoice(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return transf.combine.Choice(l, r)
		
	def transfGuardedChoice(self, l, m, r):
		l = self.transf(l)
		m = self.transf(m)
		r = self.transf(r)
		return transf.combine.GuardedChoice(l, m, r)
		
	def transfTransf(self, n):
		n = self.id(n)
		txn = self.bind_name(n)
		if txn is None:
			raise SemanticException(n, "could not find %s" % n)
		if not isinstance(txn, transf.base.Transformation):
			raise SemanticException(n, "%s is not a transformation" % n)
		return txn
		
	def transfTransfFac(self, i, a):
		n = self.id(i)
		a = map(self.arg, a)
		
		Txn = self.bind_name(n)
		if Txn is None:
			raise SemanticException(i, "could not find %s" % n)
		if not callable(Txn):
			raise SemanticException(i, "%s is not callable" % n)
		try:
			txn = Txn(*a)
		except TypeError, ex:
			raise SemanticException(i, "error: %s" % ex)
		if not isinstance(txn, transf.base.Transformation):
			raise SemanticException(i, "%s did not return a transformation" % n)
		return txn
	
	def transfScope(self, vars, t):
		vars = self.id_list(vars)
		t = self.transf(t)
		if vars:
			return transf.scope.Local(t, vars)
		else:
			return t

	def transfRule(self, m, b):
		m = self.match(m)
		b = self.build(b)
		return transf.combine.Composition(m, b)
		
	def transfRuleWhere(self, m, b, w):
		m = self.match(m)
		b = self.match(b)
		w = self.transf(w)
		return transf.combine.Composition(m, transf.combine.Composition(transf.combine.Where(w), b))
		
	def transfAnon(self, r):
		vars = []
		self.collect(r, vars)
		r = self.transf(r)
		if vars:
			r = transf.scope.Local(r, vars)
		return r
	
	def transfStore(self, t, v):
		t = self.transf(t)
		v = self.id(v)
		return transf.combine.Where(transf.combine.Composition(t, transf.variable.Set(v)))
	
	def transfBuildApply(self, t, b):
		t = self.transf(t)
		b = self.build(b)
		return transf.combine.Composition(b, t)
		
	def transfIf(self, conds, other):
		conds = map(self.doIfClause, conds)
		other = self.transf(other)
		return transf.combine.IfElifElse(conds, other)

	def doIfClause(self, t):
		c, a = t.rmatch("IfClause(_, _)")
		c = self.transf(c)
		a = self.transf(a)
		return (c, a)
		
	def transfSwitch(self, expr, cases, other):
		expr = self.transf(expr)
		cases = map(self.doSwitchClause, cases)
		other = self.transf(other)
		return transf.combine.Switch(expr, cases, other)

	def doSwitchClause(self, t):
		c, a = t.rmatch("SwitchCase(_, _)")
		c = map(self.static, c)
		a = self.transf(a)
		return (c, a)
		
	def transfLet(self, v, t):
		v = map(self.doLetDef, v)
		t = self.transf(t)
		v = dict(v)
		return transf.scope.Let(t, **v)

	def doLetDef(self, t):
		i, t = t.rmatch("LetDef(_,_)")
		i = self.id(i)
		t = self.transf(t)
		return (i, t)
		
	def transfJoin(self, l, r, u, i):	
		l = self.transf(l)
		r = self.transf(r)
		u = self.id_list(u)
		i = self.id_list(i)
		return transf.table.Join(l, r, u, i)
		
	def transfIterate(self, o, u, i):	
		o = self.transf(o)
		u = self.id_list(u)
		i = self.id_list(i)
		return transf.table.Iterate(o, u, i)

	def transfRec(self, i, t):
		i = self.id(i)
		ret = transf.util.Proxy()
		self.stack.append({i: ret})
		t = self.transf(t)
		self.stack.pop()
		ret.subject = t
		return ret

	# #( VARMETHOD v=id m=id a=arg_list )
	#	{ ret = transf.variable.Wrap(v, m, *a) }
	
	def transfWith(self, vs, t):
		vs = map(self.doWithDef, vs)
		t = self.transf(t)
		return transf.scope.With(vs, t)

	def doWithDef(self, t):
		v, c = t.rmatch("WithDef(_,_)")
		v = self.id(v)
		c = self.constructor(c)
		return (v, c)


	def arg(self, arg):
		return self._dispatch(arg, 'arg')
	
	def argObj(self, o):
		o = self._str(o)
		return eval(o, self.globals, self.locals)
	
	def argVar(self, v):
		v = self._str(v)
		return v
	
	def arg_Term(self, t):
		return self.transf(t)


	def constructor(self, c):
		return self._dispatch(c, 'constructor')
		
	def constructorTermTransf(self, t):
		t = self.transf(t)
		return transf.term.Transf(t)

	def constructorTerm(self):
		return transf.term.new
		
	def constructorTableCopy(self, v):
		v = self.id(v)
		return transf.table.Copy(v)

	def constructorTable(self):
		return transf.table.new


	def static(self, t):
		return self._dispatch(t, 'static')
		
	def staticInt(self, i):
		i = self._int(i)
		return aterm.factory.factory.makeInt(i)
	
	def staticReal(self, r):
		r = self._real(r)
		return aterm.factory.factory.makeReal(r)
	
	def staticStr(self, s):
		s = self._str(s)
		return aterm.factory.factory.makeStr(s)
	
	def staticNil(self):
		return aterm.factory.factory.makeNil()
	
	def staticCons(self, h, t):
		h = self.static(h)
		t = self.static(t)
		return aterm.factory.factory.makeCons(h, t)
	
	def staticUndef(self):
		return aterm.factory.factory.makeNil()
		
	def staticAppl(self, n, a):
		n = self.static(n)
		a = self.static(a)
		return aterm.factory.factory.makeAppl(n, a)
		
	def staticWildcard(self):
		raise SemanticException(None, "wildcard in static term")

	def staticVar(self, v):
		raise SemanticException(None, "variable in static term")

	def staticTransf(self, t):
		raise SemanticException(None, "transformation in static term")

	def staticAnnos(self, t, a):
		t = self.static(t)
		a = self.static(a)
		return t.setAnnotations(a)


	def match(self, t):
		return self._dispatch(t, 'match')
		
	def matchInt(self, i):
		i = self._int(i)
		return transf.match.Int(i)
	
	def matchReal(self, r):
		r = self._real(r)
		return transf.match.Real(r)
	
	def matchStr(self, s):
		s = self._str(s)
		return transf.match.Str(s)
	
	def matchNil(self):
		return transf.match.nil
	
	def matchCons(self, h, t):
		h = self.match(h)
		t = self.match(t)
		return transf.match.Cons(h, t)
	
	def matchUndef(self):
		return transf.base.ident
		
	def matchAppl(self, n, a):
		n = self.match(n)
		a = self.match(a)
		return transf.match.Appl(n, a)
		
	def matchWildcard(self):
		return transf.base.ident

	def matchVar(self, v):
		v = self._str(v)
		return transf.match.Var(v)

	def matchTransf(self, t):
		t = self.transf(t)
		return t

	def matchAnnos(self, t, a):
		t = self.match(t)
		a = self.match(a)
		return transf.combine.Composition(t, transf.match.Annos(a))

	
	def build(self, t):
		return self._dispatch(t, 'build')
		
	def buildInt(self, i):
		i = self._int(i)
		return transf.build.Int(i)
	
	def buildReal(self, r):
		r = self._real(r)
		return transf.build.Real(r)
	
	def buildStr(self, s):
		s = self._str(s)
		return transf.build.Str(s)
	
	def buildNil(self):
		return transf.build.nil
	
	def buildCons(self, h, t):
		h = self.build(h)
		t = self.build(t)
		return transf.build.Cons(h, t)
	
	def buildUndef(self):
		return transf.build.nil
		
	def buildAppl(self, n, a):
		n = self.build(n)
		a = self.build(a)
		return transf.build.Appl(n, a)
		
	def buildWildcard(self):
		return transf.base.ident

	def buildVar(self, v):
		v = self._str(v)
		return transf.build.Var(v)

	def buildTransf(self, t):
		t = self.transf(t)
		return t

	def buildAnnos(self, t, a):
		t = self.build(t)
		a = self.build(a)
		return transf.combine.Composition(t, transf.build.Annos(a))



	
	def traverse(self, t):
		return self._dispatch(t, 'traverse')
		
	def traverseInt(self, i):
		i = self._int(i)
		return transf.match.Int(i)
	
	def traverseReal(self, r):
		r = self._real(r)
		return transf.match.Real(r)
	
	def traverseStr(self, s):
		s = self._str(s)
		return transf.match.Str(s)
	
	def traverseNil(self):
		return transf.match.nil
	
	def traverseCons(self, h, t):
		h = self.traverse(h)
		t = self.traverse(t)
		return transf.congruent.Cons(h, t)
	
	def traverseUndef(self):
		return transf.base.ident
		
	def traverseAppl(self, n, a):
		n = self.traverse(n)
		a = self.traverse(a)
		return transf.congruent.Appl(n, a)
		
	def traverseWildcard(self):
		return transf.base.ident

	def traverseVar(self, v):
		v = self._str(v)
		return transf.congruent.Var(v)

	def traverseTransf(self, t):
		t = self.transf(t)
		return t

	def traverseAnnos(self, t, a):
		t = self.traverse(t)
		a = self.traverse(a)
		return transf.combine.Composition(t, transf.traverse.Annos(a))


	def collect(self, t, vars):
		self._dispatch(t, 'collect', vars = vars)
		
	def collectRule(self, m, b, vars):
		self.collect(m, vars)

	def collectWhereRule(self, m, b, w, vars):
		self.collect(m, vars)

	def collectCons(self, h, t, vars):
		self.collect(h, vars)
		self.collect(t, vars)
	
	def collectAppl(self, n, a, vars):
		self.collect(n, vars)
		self.collect(a, vars)
		
	def collectVar(self, v, vars):
		v = self._str(v)
		if v not in vars:
			vars.append(v)
			
	def collectAnnosVar(self, t, a, vars):
		self.collect(t, vars)
		self.collect(a, vars)

	def collect_Term(self, t, vars):
		# ignore everything else
		pass


	def id_list(self, l):
		return map(self.id, l)

	def id(self, i):
		return self._str(i)
