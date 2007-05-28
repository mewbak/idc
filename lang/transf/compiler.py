"""Translates the transformation describing aterms into the
respective transformation objects."""


# pylint: disable-msg=R0201

from aterm import walker


class SemanticException(Exception):

	pass


MATCH, BUILD, TRAVERSE = range(3)
ARG, LOCAL, GLOBAL = range(3)


class Compiler(walker.Walker):

	def __init__(self):
		self.stmts = []
		self.indent = 0
		self.vars = {}

	def stmt(self, s):
		self.stmts.append('\t' * self.indent + s)

	def compile(self, t):
		self.define(t)
		return "\n".join(self.stmts)

	definitions = compile

	define = walker.Dispatch('define')

	def defineDefs(self, tdefs):
		for tdef in tdefs:
			self.vars = {}
			self.define(tdef)

	def defineVarDef(self, n, t):
		n = self.id(n)
		t = self.type(t)
		self.stmt("%s = %s(%r)" % (n, t, n))

	def type(self, t):
		t = self.id(t)
		if t == "Term":
			return "transf.types.term.Term"
		if t == "Table":
			return "transf.types.table.Table"
		raise SemanticException

	def defineTransfDef(self, n, t):
		n = self.id(n)
		t = self.doTransf(t)
		self.stmt("%s = %s" % (n, t))

	def defineMacroDef(self, n, a, t):
		n = self.id(n)
		a = self.id_list(a)
		for a_ in a:
			self.vars[a_] = ARG
		a = ",".join(a)
		try:
			n.index(".")
		except ValueError:
			self.stmt("def %s(%s):" % (n, a))
			self.indent += 1
			t = self.doTransf(t)
			self.stmt("return %s" % t)
			self.indent -= 1
		else:
			# XXX: hack for proxy to work
			self.stmt("def _tmp(%s):" % a)
			self.indent += 1
			t = self.doTransf(t)
			self.stmt("return %s" % t)
			self.indent -= 1
			self.stmt("%s = _tmp" % n)

	def doTransf(self, t):
		t = self.transf(t)
		vs = []
		for vn, vt in self.vars.iteritems():
			if vt == LOCAL:
				vs.append(vn)
		vs = "[" + ",".join(["_" + v for v in vs]) + "]"
		return "transf.lib.scope.Scope(%s, %s)" % (vs, t)

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
		v = self.var(v)
		return "%s.set" % v

	def transfUnset(self, v):
		v = self.var(v)
		return "%s.unset" % v

	def transfComposition(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return "transf.lib.combine.Composition(%s, %s)" % (l, r)

	def transfChoice(self, o):
		# FIXME: insert a variable scope here
		o = "[" + ",".join(["%s" % self.transf(_o) for _o in o]) + "]"
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

	def transfMacro(self, i, a):
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

	def transfApplyMatch(self, t, m):
		t = self.transf(t)
		m = self.match(m)
		return "transf.lib.combine.Composition(%s, %s)" % (t, m)

	def transfApplyStore(self, t, v):
		t = self.transf(t)
		v = self.id(v)
		return "transf.lib.combine.Where(transf.lib.combine.Composition(%s, %s.set))" % (t, v)

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
		# FIXME: add i to the var list as ARG
		t = self.transf(t)
		return "transf.lib.iterate.Rec(lambda %s: %s)" % (i, t)

	def transfGlobal(self, vs, t):
		oldvars = {}
		vs = self.id_list(vs)
		for v in vs:
			if v in self.vars:
				oldvars[v] = self.vars[v]
			self.vars[v] = GLOBAL
		t = self.transf(t)
		self.vars.update(oldvars)
		return t

	def transfWith(self, vs, t):
		vs = map(self.transf, vs)
		vs.reverse()
		t = self.transf(t)
		for v in vs:
			t = "transf.lib.combine.Composition(%s, %s)" % (v, t)
		return t

	def transfWithDef(self, v, t):
		v = self.var(v)
		t = self.transf(t)
		return "transf.lib.combine.Where(transf.lib.combine.Composition(%s, %s.set))" % (t, v)

	arg = walker.Dispatch('arg')

	def argObj(self, o):
		o = self._str(o)
		return o

	def argVar(self, v):
		v = self._str(v)
		return repr(v)

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
		n = self._str(n)
		a = self.static(a)
		return "aterm.factory.factory.makeAppl(%r, %s)" % (n, a)

	def staticApplName(self, n):
		n = self._str(n)
		return "aterm.factory.factory.makeAppl(%r)" % (n)

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
		v = self.var(v)
		if mode == MATCH:
			return "transf.lib.match.Var(%s)" % v
		elif mode == BUILD:
			return "transf.lib.build.Var(%s)" % v
		elif mode == TRAVERSE:
			return "transf.lib.congruent.Var(%s)" % v

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

	def collectVar(self, name, vars):
		name = self.id(name)
		vars.add(name)

	collectSet = collectVar
	collectUnset = collectVar

	def collectWithDef(self, name, t, vars):
		name = self.id(name)
		vars.add(name)

	def collectGlobal(self, names, operand, vars):
		names = self.id_list(names)
		for name in names:
			vars.discard(name)
		self.collect(operand)

	def collect_List(self, elms, vars):
		for elm in elms:
			self.collect(elm, vars)

	def collect_Appl(self, name, args, vars):
		for arg in args:
			self.collect(arg, vars)

	def collect_Term(self, t, vars):
		# ignore everything else
		pass


	def var(self, v):
		v = self._str(v)
		if not v in self.vars:
			self.stmt('_%s = transf.types.term.Term(%r)' %(v, v))
			self.vars[v] = LOCAL
			return self.local(v)
		else:
			if self.vars[v] == LOCAL:
				return self.local(v)
			else:
				return v

	def local(self, v):
		return "_" + v


	def id_list(self, l):
		return map(self.id, l)

	def id(self, i):
		s = self._str(i)
		parts = s.split('.')
		head = parts[0]
		tail = parts[1:]
		if head in self.vars and self.vars[head] == LOCAL:
			return ".".join([self.local(s)] + tail)
		else:
			return s
