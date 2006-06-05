'''Term rewriting transformations.'''


import aterm.factory
import aterm.visitor

from transf import exception
from transf import base
from transf import match
from transf import build
from transf import scope


_factory = aterm.factory.Factory()


class _VarCollector(aterm.visitor.Visitor):
	
	def __init__(self):
		aterm.visitor.Visitor.__init__(self)
		self.vars = []
	
	def visitLit(self, term, *args, **kargs):
		pass
		
	def visitNil(self, term, *args, **kargs):
		pass

	def visitCons(self, term, *args, **kargs):
		self.visit(term.head)
		self.visit(term.tail)

	def visitAppl(self, term, *args, **kargs):
		self.visit(term.name)
		self.visit(term.args)

	def visitWildcard(self, term, *args, **kargs):
		pass

	def visitVar(self, term, *args, **kargs):
		self.vars.append(term.name)


def Rule(match_pattern, build_pattern, locals = None):
	
	if locals is None:
		if isinstance(match_pattern, basestring):
			match_pattern = _factory.parse(match_pattern)
		varcollector = _VarCollector()
		varcollector.visit(match_pattern)
		locals = varcollector.vars
		
	return scope.Scope(match.MatchPattern(match_pattern) & build.BuildPattern(build_pattern), locals)


def RuleSet(patterns, locals = None):
	rules = base.Fail()
	for match_pattern, build_pattern in patterns:
		rules = rules | Rule(match_pattern, build_pattern, locals)
	return rules

