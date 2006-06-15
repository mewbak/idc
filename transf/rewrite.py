'''Term rewriting transformations.'''


__docformat__ = 'epytext'


import aterm.factory
import aterm.terms
import aterm.visitor

from transf import exception
from transf import base
from transf import _operate
from transf import match
from transf import build
from transf import scope


_factory = aterm.factory.Factory()


class _VarCollector(aterm.visitor.Visitor):

	def collect(cls, term, vars):
		collector = _VarCollector(vars)
		collector.visit(term)
	collect = classmethod(collect)

	def __init__(self, vars):
		aterm.visitor.Visitor.__init__(self)
		self.vars = vars
	
	def visit(self, term):
		aterm.visitor.Visitor.visit(self, term)
		if term.annotations:
			self.visit(self, term.annotations)
		
	def visitLit(self, term):
		pass
		
	def visitNil(self, term):
		pass

	def visitCons(self, term):
		self.visit(term.head)
		self.visit(term.tail)

	def visitAppl(self, term):
		self.visit(term.name)
		self.visit(term.args)

	def visitWildcard(self, term):
		pass

	def visitVar(self, term):
		self.vars.append(term.name)
	

def _Coerce(transf, Term, Pattern, locals = None):
	if isinstance(transf, basestring):
		transf = _factory.parse(transf)
	if isinstance(transf, aterm.terms.Term):
		if transf.isConstant():
			transf = Term(transf)
		else:
			if locals is not None:
				_VarCollector.collect(transf, locals)
			transf = Pattern(transf)
	elif not isinstance(transf, base.Transformation):
		raise TypeError('not a transformation', transf)
	return transf


def Term(match_term, build_transf):
	match_transf = match.Term(match_term)
	build_transf = _Coerce(build_transf, build.Term, build.Pattern, [])
	return match_transf & build_transf


class TermSet(base.Transformation):
	
	def __init__(self, seq):
		base.Transformation.__init__(self)
		self.transfs = {}
		
		try:
			it = seq.iteritems()
		except AttributeError:
			it = iter(seq)

		for match_term, build_transf in it:
			if isinstance(match_term, basestring):
				match_term = _factory.parse(match_term)
			build_transf = _Coerce(build_transf, build.Term, build.Pattern, [])
			self.transfs[match_term] = build_transf
		
	def apply(self, term, ctx):
		try:
			build_transf = self.transfs[term]
		except KeyError:
			raise exception.Failure('term not in set', term)
		else:
			return build_transf.apply(term, ctx)
			

def Pattern(match_transf, build_transf, locals = None):
	if locals is None:
		locals = []
		match_transf = _Coerce(match_transf, match.Term, match.Pattern, locals)
	else:
		match_transf = _Coerce(match_transf, match.Term, match.Pattern)
	build_transf = _Coerce(build_transf, build.Term, build.Pattern)
	rule = match_transf & build_transf
	if locals:
		rule = scope.Local(rule, locals)
	return rule


def PatternSeq(seq, locals = None):
	if locals is None:
		l = None
	else:
		l = []
	rules = _operate.Nary(seq, 
		lambda (m, b), r: Pattern(m, b, l) | r,
		base.fail
	)
	if locals:
		rules = scope.Local(rules, locals)
	return rules
