

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
		return translator.translate(self.term)


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
		from transf.parse import builtins
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
	transf = translate
	meta_def = translate
	
	def translateApplDefs(self, tdefs):
		for tdef in tdefs:
			self.translate(tdef)
	
	def translateApplTransfDef(self, n, t):
		n = self.id(n)
		t = self.translate(t)
		self.define_name(n, t)

	def translateApplTransfFacDef(self, n, a, t):
		n = self.id(n)
		T = self.meta(a, t)
		self.define_name(n, T)
	
	def translateApplMetaDef(self, a, t):
		return self.meta(a, t)

	def meta(self, a, t):
		a = map(self.id, a)
		return Meta(
			self.globals,
			self.locals,
			a,
			t,
		)
	
	def translateApplIdent(self):
		return transf.base.ident
		
	def translateApplFail(self):
		return transf.base.fail

	def translateApplMatch(self, t):
		return self.match(t)
		
	def translateApplBuild(self, t):
		return self.build(t)
		
	def translateApplTraverse(self, t):
		return self.traverse(t)
		
	def translateApplSet(self, v):
		v = self.var(v)
		return transf.variable.Set(v)

	def translateApplUnset(self, v):
		v = self.var(v)
		return transf.variable.Unset(v)
		
	def translateApplComposition(self, l, r):
		l = self.translate(l)
		r = self.translate(r)
		return transf.combine.Composition(l, r)
		
	def translateApplChoice(self, l, r):
		l = self.translate(l)
		r = self.translate(r)
		return transf.combine.Choice(l, r)
		
	def translateApplLeftChoice(self, l, r):
		l = self.translate(l)
		r = self.translate(r)
		return transf.combine.Choice(l, r)
		
	def translateApplGuardedChoice(self, l, m, r):
		l = self.translate(l)
		m = self.translate(m)
		r = self.translate(r)
		return transf.combine.GuardedChoice(l, m, r)
		
	def translateApplTransf(self, n):
		n = self.id(n)
		txn = self.bind_name(n)
		if txn is None:
			raise SemanticException(n, "could not find %s" % n)
		if not isinstance(txn, transf.base.Transformation):
			raise SemanticException(n, "%s is not a transformation" % n)
		return txn
		
	def translateApplTransfFac(self, i, a):
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
	
	def translateApplScope(self, vars, t):
		vars = self.id_list(vars)
		t = self.translate(t)
		if vars:
			return transf.scope.Local(t, vars)
		else:
			return t

	def translateApplRule(self, m, b):
		m = self.match(m)
		b = self.build(b)
		return transf.combine.Composition(m, b)
		
	def translateApplWhereRule(self, m, b, w):
		m = self.match(m)
		b = self.match(b)
		w = self.translate(w)
		return transf.combine.Composition(m, transf.combine.Composition(transf.combine.Where(w), b))
		
	def translateApplAnon(self, r):
		vars = []
		self.collect(r, vars)
		r = self.translate(r)
		if vars:
			r = transf.scope.Local(r, vars)
		return r
	
	def translateApplStore(self, t, v):
		t = self.translate(t)
		v = self.var(v)
		return transf.combine.Where(transf.combine.Composition(t, transf.variable.Set(v)))
	
	def translateApplBuildApply(self, t, b):
		t = self.translate(t)
		b = self.build(b)
		return transf.combine.Composition(b, t)
		
	def translateApplIf(self, conds, other):
		conds = map(self.translate, conds)
		other = self.translate(other)
		return transf.combine.IfElifElse(conds, other)

	def translateApplIfClause(self, c, a):
		c = self.translate(c)
		a = self.translate(a)
		return (c, a)
		
	def translateApplSwitch(self, expr, cases, other):
		expr = self.translate(expr)
		cases = map(self.translate, cases)
		other = self.translate(other)
		return transf.combine.Switch(expr, cases, other)

	def translateApplSwitchCase(self, c, a):
		c = tuple(map(self.static, c))
		a = self.translate(a)
		return (c, a)
		
	def translateApplLet(self, v, t):
		v = map(self.translate, v)
		t = self.translate(t)
		v = dict(v)
		return transf.scope.Let(t, **v)

	def translateApplJoin(self, l, r, u, i):	
		l = self.translate(l)
		r = self.translate(r)
		u = self.id_list(u)
		i = self.id_list(i)
		return transf.table.Join(l, r, u, i)
		
	def translateApplIterate(self, o, u, i):	
		o = self.translate(o)
		u = self.id_list(u)
		i = self.id_list(i)
		return transf.table.Iterate(o, u, i)

	def translateApplRec(self, i, t):
		i = self.id(i)
		ret = transf.util.Proxy()
		self.stack.append({i: ret})
		t = self.translate(t)
		self.stack.pop()
		ret.subject = t
		return ret

	# #( VARMETHOD v=id m=id a=arg_list )
	#	{ ret = transf.variable.Wrap(v, m, *a) }
	
	def translateApplWith(self, vs, t):
		vs = map(self.translate, vs)
		t = self.translate(t)
		return transf.scope.With(vs, t)

	def translateApplLetDef(self, i, t):
		i = self.id(i)
		t = self.transf(t)
		return (i, t)
		
	def arg(self, arg):
		return self._dispatch(arg, 'arg')
	
	def argApplObj(self, o):
		o = self._str(o)
		return eval(o, self.globals, self.locals)
	
	def argApplVar(self, v):
		v = self._str(v)
		return v
	
	def argTerm(self, t):
		return self.translate(t)

	def translateApplVarDef(self, v, c):
		v = self.var(v)
		c = self.constructor(c)
		return (v, c)

	def constructor(self, c):
		return self._dispatch(c, 'constructor')
		
	def constructorApplTermTransf(self, t):
		t = self.translate(t)
		return transf.term.Transf(t)

	def constructorApplTerm(self):
		return transf.term.new
		
	def constructorApplTableCopy(self, v):
		v = self.var(v)
		return transf.table.Copy(v)

	def constructorApplTable(self):
		return transf.table.new


	def static(self, t):
		return self._dispatch(t, 'static')
		
	def staticApplInt(self, i):
		return i
	
	def staticApplReal(self, r):
		return r
	
	def staticApplStr(self, s):
		return s
	
	def staticApplNil(self):
		return aterm.factory.factory.makeNil()
	
	def staticApplCons(self, h, t):
		h = self.static(h)
		t = self.static(t)
		return aterm.factory.factory.makeCons(h, t)
	
	def staticApplUndef(self):
		return aterm.factory.factory.makeNil()
		
	def staticApplAppl(self, n, a):
		n = self.static(n)
		a = self.static(a)
		return aterm.factory.factory.makeAppl(n, a)
		
	def staticApplWildcard(self):
		raise SemanticException(None, "wildcard in static term")

	def staticApplVar(self, v):
		raise SemanticException(None, "variable in static term")

	def staticApplTransf(self, t):
		raise SemanticException(None, "transformation in static term")

	def staticApplAnnos(self, t, a):
		t = self.static(t)
		a = self.static(a)
		return t.setAnnotations(a)


	def match(self, t):
		return self._dispatch(t, 'match')
		
	def matchApplInt(self, i):
		i = self._int(i)
		return transf.match.Int(i)
	
	def matchApplReal(self, r):
		r = self._real(r)
		return transf.match.Real(r)
	
	def matchApplStr(self, s):
		s = self._str(s)
		return transf.match.Str(s)
	
	def matchApplNil(self):
		return transf.match.nil
	
	def matchApplCons(self, h, t):
		h = self.match(h)
		t = self.match(t)
		return transf.match.Cons(h, t)
	
	def matchApplUndef(self):
		return transf.base.ident
		
	def matchApplAppl(self, n, a):
		n = self.match(n)
		a = self.match(a)
		return transf.match.Appl(n, a)
		
	def matchApplWildcard(self):
		return transf.base.ident

	def matchApplVar(self, v):
		v = self._str(v)
		return transf.match.Var(v)

	def matchApplTransf(self, t):
		t = self.translate(t)
		return t

	def matchApplAnnos(self, t, a):
		t = self.match(t)
		a = self.match(a)
		return transf.combine.Composition(t, transf.match.Annos(a))

	
	def build(self, t):
		return self._dispatch(t, 'build')
		
	def buildApplInt(self, i):
		i = self._int(i)
		return transf.build.Int(i)
	
	def buildApplReal(self, r):
		r = self._real(r)
		return transf.build.Real(r)
	
	def buildApplStr(self, s):
		s = self._str(s)
		return transf.build.Str(s)
	
	def buildApplNil(self):
		return transf.build.nil
	
	def buildApplCons(self, h, t):
		h = self.build(h)
		t = self.build(t)
		return transf.build.Cons(h, t)
	
	def buildApplUndef(self):
		return transf.build.nil
		
	def buildApplAppl(self, n, a):
		n = self.build(n)
		a = self.build(a)
		return transf.build.Appl(n, a)
		
	def buildApplWildcard(self):
		return transf.base.ident

	def buildApplVar(self, v):
		v = self._str(v)
		return transf.build.Var(v)

	def buildApplTransf(self, t):
		t = self.translate(t)
		return t

	def buildApplAnnos(self, t, a):
		t = self.build(t)
		a = self.build(a)
		return transf.combine.Composition(t, transf.build.Annos(a))



	
	def traverse(self, t):
		return self._dispatch(t, 'traverse')
		
	def traverseApplInt(self, i):
		i = self._int(i)
		return transf.match.Int(i)
	
	def traverseApplReal(self, r):
		r = self._real(r)
		return transf.match.Real(r)
	
	def traverseApplStr(self, s):
		s = self._str(s)
		return transf.match.Str(s)
	
	def traverseApplNil(self):
		return transf.match.nil
	
	def traverseApplCons(self, h, t):
		h = self.traverse(h)
		t = self.traverse(t)
		return transf.congruent.Cons(h, t)
	
	def traverseApplUndef(self):
		return transf.base.ident
		
	def traverseApplAppl(self, n, a):
		n = self.traverse(n)
		a = self.traverse(a)
		return transf.congruent.Appl(n, a)
		
	def traverseApplWildcard(self):
		return transf.base.ident

	def traverseApplVar(self, v):
		v = self._str(v)
		return transf.congruent.Var(v)

	def traverseApplTransf(self, t):
		t = self.translate(t)
		return t

	def traverseApplAnnos(self, t, a):
		t = self.traverse(t)
		a = self.traverse(a)
		return transf.combine.Composition(t, transf.traverse.Annos(a))


	def collect(self, t, vars):
		self._dispatch(t, 'collect', vars = vars)
		
	def collectApplRule(self, m, b, vars):
		self.collect(m, vars)

	def collectApplCons(self, h, t, vars):
		self.collect(h, vars)
		self.collect(t, vars)
	
	def collectApplAppl(self, n, a, vars):
		self.collect(n, vars)
		self.collect(a, vars)
		
	def collectApplVar(self, v, vars):
		v = self._str(v)
		if v not in vars:
			vars.append(v)
			
	def collectAnnosVar(self, t, a, vars):
		self.collect(t, vars)
		self.collect(a, vars)

	def collectTerm(self, t, vars):
		pass

	def id_list(self, l):
		return map(self.id, l)

	def id(self, v):
		return self._dispatch(v, "id")
	
	def idApplId(self, i):
		return self._str(i)

	def var(self, v):
		return self._dispatch(v, "var")
	
	def varApplVar(self, v):
		return self._str(v)
