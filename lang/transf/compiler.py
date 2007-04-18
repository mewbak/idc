"""Translates the transformation describing aterms into the
respective transformation objects."""


# pylint: disable-msg=R0201


import antlr

import aterm.factory
from aterm import walker

import transf.transformation
import transf.types.variable
import transf.types.term
import transf.types.table
import transf.lib


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


MATCH, BUILD, TRAVERSE = range(3)


class Compiler(walker.Walker):

	def __init__(self):
		pass

	compile = walker.Dispatch('compile')

	transf_defs = compile
	meta_def = compile

	def compileDefs(self, tdefs):
		stmts = []
		for tdef in tdefs:
			stmts.append(self.compile(tdef) + "\n")
		return "".join(stmts)

	def compileTransfDef(self, n, t):
		n = self.id(n)
		t = self.transf(t)
		return "%s = %s" % (n, t)

	def compileTransfFacDef(self, n, a, t):
		n = self.id(n)
		T = self.meta(a, t)
		return "%s = %s" % (n, T)

	def compileMetaDef(self, a, t):
		return self.meta(a, t)


	def meta(self, a, t):
		a = ",".join(map(self.id, a))
		t = self.transf(t)
		return "lambda %s: %s" % (a, t)


	transf = walker.Dispatch('transf')

	def transfIdent(self):
		return "transf.lib.base.ident"

	def transfFail(self):
		return "transf.lib.base.fail"

	def transfMatch(self, t):
		return self.match(t)

	def transfBuild(self, t):
		return self.build(t)

	def transfTraverse(self, t):
		return self.traverse(t)

	def transfSet(self, v):
		v = self.id(v)
		return "transf.types.variable.Set(%r)" % v

	def transfUnset(self, v):
		v = self.id(v)
		return "transf.types.variable.Unset(%r)" % v

	def transfComposition(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return "transf.lib.combine.Composition(%s, %s)" % (l, r)

	def transfChoice(self, o):
		o = "[" + ",".join(map(self.transf, o)) + "]"
		return "transf.lib.combine.UndeterministicChoice(%s)" % o

	def transfLeftChoice(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return "transf.lib.combine.Choice(%s, %s)" % (l, r)

	def transfGuardedChoice(self, l, m, r):
		l = self.transf(l)
		m = self.transf(m)
		r = self.transf(r)
		return "transf.lib.combine.GuardedChoice(%s, %s, %s)" % (l, m, r)

	def transfTransf(self, n):
		n = self.id(n)
		return n

	def transfTransfFac(self, i, a):
		n = self.id(i)
		a = ",".join(map(self.arg, a))
		return "%s(%s)" % (n, a)

	def transfRule(self, m, b):
		m = self.match(m)
		b = self.build(b)
		return "transf.lib.combine.Composition(%s, %s)" % (m, b)

	def transfRuleWhere(self, m, b, w):
		m = self.match(m)
		b = self.match(b)
		w = self.transf(w)
		return "transf.lib.combine.Composition(%s, transf.lib.combine.Composition(lib.transf.combine.Where(%s), %s))" % (m, w, b)

	def transfAnon(self, r):
		vars = []
		self.collect(r, vars)
		r = self.transf(r)
		if vars:
			r = "transf.lib.scope.Local([%s], %s)" % (",".join(vars), r)
		return r

	def transfApplyMatch(self, t, m):
		t = self.transf(t)
		m = self.match(m)
		return "transf.lib.combine.Composition(%s, %s)" % (t, m)

	def transfApplyStore(self, t, v):
		t = self.transf(t)
		v = self.id(v)
		return "transf.lib.combine.Where(transf.lib.combine.Composition(%s, transf.types.variable.Set(%r)))" % (t, v)

	def transfBuildApply(self, t, b):
		t = self.transf(t)
		b = self.build(b)
		return "transf.lib.combine.Composition(%s, %s)" % (b, t)

	def transfIf(self, conds, other):
		conds = "[" + ",".join(map(self.doIfClause, conds)) + "]"
		other = self.transf(other)
		return "transf.lib.combine.IfElifElse(%s, %s)" % (conds, other)

	def doIfClause(self, t):
		c, a = t.rmatch("IfClause(_, _)")
		c = self.transf(c)
		a = self.transf(a)
		return "(%s, %s)" % (c, a)

	def transfSwitch(self, expr, cases, other):
		expr = self.transf(expr)
		cases = "[" + ",".join(map(self.doSwitchClause, cases)) + "]"
		other = self.transf(other)
		return "transf.lib.combine.Switch(%s, %s, %s)" % (expr, cases, other)

	def doSwitchClause(self, t):
		c, a = t.rmatch("SwitchCase(_, _)")
		c = "[" + ",".join(map(self.static, c)) + "]"
		a = self.transf(a)
		return "(%s, %s)" % (c, a)

	def transfJoin(self, l, r, u, i):
		l = self.transf(l)
		r = self.transf(r)
		u = self.id_list(u)
		i = self.id_list(i)
		return "transf.types.table.Join(%s, %s, %s, %s)" % (l, r, u, i)

	def transfIterate(self, o, u, i):
		o = self.transf(o)
		u = self.id_list(u)
		i = self.id_list(i)
		return "transf.types.table.Iterate(%s, %s, %s)" % (o, u, i)

	def transfRec(self, i, t):
		i = self.id(i)
		return "transf.lib.iterate.Rec(lambda %s: %s)" % (i, t)

	# #( VARMETHOD v=id m=id a=arg_list )
	#	{ ret = transf.types.variable.Wrap(v, m, *a) }

	def transfWith(self, vs, t):
		vs = map(self.doWithDef, vs)
		t = self.transf(t)
		return "transf.lib.scope.With(%s, %s)" % (vs, t)

	def doWithDef(self, t):
		v, c = t.rmatch("WithDef(_,_)")
		v = self.id(v)
		c = self.constructor(c)
		return "(%r, %s)" % (v, c)


	arg = walker.Dispatch('arg')

	def argObj(self, o):
		o = self._str(o)
		return eval(o, self.globals, self.locals)

	def argVar(self, v):
		v = self._str(v)
		return v

	def arg_Term(self, t):
		return self.transf(t)


	constructor = walker.Dispatch('constructor')

	def constructorTermTransf(self, t):
		t = self.transf(t)
		return "transf.types.term.Transf(%s)" % t

	def constructorTerm(self):
		return "transf.types.term.new"

	def constructorTableCopy(self, v):
		v = self.id(v)
		return "transf.types.table.Copy(%r)" % v

	def constructorTable(self):
		return "transf.types.table.new"


	static = walker.Dispatch('static')

	def staticInt(self, i):
		i = self._int(i)
		return "aterm.factory.factory.makeInt(%r)" % i

	def staticReal(self, r):
		r = self._real(r)
		return "aterm.factory.factory.makeReal(%r)" % r

	def staticStr(self, s):
		s = self._str(s)
		return "aterm.factory.factory.makeStr(%r)" % s

	def staticNil(self):
		return "aterm.factory.factory.makeNil()"

	def staticCons(self, h, t):
		h = self.static(h)
		t = self.static(t)
		return "aterm.factory.factory.makeCons(%s, %s)" % (h, t)

	def staticUndef(self):
		return "aterm.factory.factory.makeNil()"

	def staticAppl(self, n, a):
		n = self.static(n)
		a = self.static(a)
		return "aterm.factory.factory.makeAppl(%s.value, %s)" % (n, a)

	def staticWildcard(self):
		raise SemanticException(None, "wildcard in static term")

	def staticVar(self, v):
		raise SemanticException(None, "variable in static term")

	def staticTransf(self, t):
		raise SemanticException(None, "transformation in static term")

	def staticAnnos(self, t, a):
		t = self.static(t)
		a = self.static(a)
		return "%s.setAnnotations(%s)" % (t, a)


	def match(self, t):
		return self.termTransf(t, mode = MATCH)

	def build(self, t):
		return self.termTransf(t, mode = BUILD)

	def traverse(self, t):
		return self.termTransf(t, mode = TRAVERSE)


	termTransf = walker.Dispatch('termTransf')

	def termTransfInt(self, i, mode):
		i = self._int(i)
		if mode == BUILD:
			return "transf.lib.build.Int(%r)" % i
		else:
			return "transf.lib.match.Int(%r)" % i

	def termTransfReal(self, r, mode):
		r = self._real(r)
		if mode == BUILD:
			return "transf.lib.build.Real(%r)" % r
		else:
			return "transf.lib.match.Real(%r)" % r

	def termTransfStr(self, s, mode):
		s = self._str(s)
		if mode == BUILD:
			return "transf.lib.build.Str(%r)" % s
		else:
			return "transf.lib.match.Str(%r)" % s

	def termTransfNil(self, mode):
		if mode == BUILD:
			return "transf.lib.build.nil"
		else:
			return "transf.lib.match.nil"

	def termTransfCons(self, h, t, mode):
		h = self.termTransf(h, mode)
		t = self.termTransf(t, mode)
		if mode == MATCH:
			return "transf.lib.match.Cons(%s, %s)" % (h, t)
		elif mode == BUILD:
			return "transf.lib.build.Cons(%s, %s)" % (h, t)
		elif mode == TRAVERSE:
			return "transf.lib.congruent.Cons(%s, %s)" % (h, t)

	def termTransfAppl(self, name, args, mode):
		name = self._str(name)
		args = "[" + ",".join([self.termTransf(arg, mode) for arg in args]) + "]"
		if mode == MATCH:
			return "transf.lib.match.Appl(%r, %s)" % (name, args)
		elif mode == BUILD:
			return "transf.lib.build.Appl(%r, %s)" % (name, args)
		elif mode == TRAVERSE:
			return "transf.lib.congruent.Appl(%r, %s)" % (name, args)

	def termTransfApplName(self, name, mode):
		name = self._str(name)
		if mode == BUILD:
			return "transf.lib.build.Appl(%r, ())" % name
		else:
			return "transf.lib.match.ApplName(%r)" % name

	def termTransfApplCons(self, n, a, mode):
		n = self.termTransf(n, mode)
		a = self.termTransf(a, mode)
		if mode == MATCH:
			return "transf.lib.match.ApplCons(%s, %s)" % (n, a)
		elif mode == BUILD:
			return "transf.lib.build.ApplCons(%s, %s)" % (n, a)
		elif mode == TRAVERSE:
			return "transf.lib.congruent.ApplCons(%s, %s)" % (n, a)

	def termTransfWildcard(self, mode):
		return "transf.lib.base.ident"

	def termTransfVar(self, v, mode):
		v = self._str(v)
		if mode == MATCH:
			return "transf.lib.match.Var(%r)" % v
		elif mode == BUILD:
			return "transf.lib.build.Var(%r)" % v
		elif mode == TRAVERSE:
			return "transf.lib.congruent.Var(%r)" % v

	def termTransfAs(self, v, t, mode):
		v = self.termTransf(v, mode)
		t = self.termTransf(t, mode)
		return "transf.lib.combine.Composition(%s, %s)" % (t, v)

	def termTransfTransf(self, t, mode):
		t = self.transf(t)
		return t

	def termTransfAnnos(self, t, a, mode):
		t = self.termTransf(t, mode)
		a = self.termTransf(a, mode)
		if mode == MATCH:
			r = "transf.lib.match.Annos(%s)" % a
		elif mode == BUILD:
			r = "transf.lib.build.Annos(%s)" % a
		elif mode == TRAVERSE:
			r = "transf.lib.traverse.Annos(%s)" % a
		return "transf.lib.combine.Composition(%s, %s)" % (t, r)

	def termTransf_Term(self, t, mode):
		# fallback to a regular transformation
		t = self.transf(t)
		return t


	collect = walker.Dispatch('collect')

	def collectRule(self, m, b, vars):
		self.collect(m, vars)

	def collectWhereRule(self, m, b, w, vars):
		self.collect(m, vars)

	def collectCons(self, h, t, vars):
		self.collect(h, vars)
		self.collect(t, vars)

	def collectAppl(self, name, args, vars):
		for arg in args:
			self.collect(arg, vars)

	def collectApplCons(self, n, a, vars):
		self.collect(n, vars)
		self.collect(a, vars)

	def collectVar(self, v, vars):
		v = self._str(v)
		if v not in vars:
			vars.append(v)

	def collectAs(self, v, t, vars):
		self.collect(v, vars)
		self.collect(t, vars)

	def collectAnnos(self, t, a, vars):
		self.collect(t, vars)
		self.collect(a, vars)

	def collect_Term(self, t, vars):
		# ignore everything else
		pass


	def id_list(self, l):
		return map(self.id, l)

	def id(self, i):
		return self._str(i)

