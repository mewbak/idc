'''Term rewriting transformations.'''


import aterm.factory
import aterm.visitor

from transf import exception
from transf import base
from transf import combinators
from transf import scope


_factory = aterm.factory.Factory()


class _Pattern(base.Transformation):
	
	
	def __init__(self, pattern):
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	

class Match(_Pattern):
	
	def apply(self, term, context):
		match = self.pattern.match(term)
		if not match:
			raise exception.Failure('pattern mismatch', self.pattern, term)

		for name, value in match.kargs.iteritems():
			try:
				prev_value = context[name]
			except KeyError:
				context[name] = value
			else:
				if not value.isEquivalent(prev_value):
					print
					print 
					print name +':', value, prev_value
					print
					raise exception.Failure

		return term


class Build(_Pattern):
	
	def apply(self, term, context):
		# FIXME: avoid the dict copy
		return self.pattern.make(term, **dict(context))
		

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
		print match_pattern
		if isinstance(match_pattern, basestring):
			match_pattern = _factory.parse(match_pattern)
		varcollector = _VarCollector()
		varcollector.visit(match_pattern)
		locals = varcollector.vars
		print locals
		print
		
	return scope.Scope(Match(match_pattern) & Build(build_pattern), locals)


def RuleSet(patterns, locals = None):
	rules = combinators.Fail()
	for match_pattern, build_pattern in patterns:
		rules = rules | Rule(match_pattern, build_pattern, locals)
	return rules

