'''Term rewriting transformations.'''


import aterm

from transf.base import *
from transf.combinators import *


class _Pattern(Transformation):
	
	_factory = aterm.Factory()
	
	def __init__(self, pattern):
		if isinstance(pattern, basestring):
			self.pattern = self._factory.parse(pattern)
		else:
			self.pattern = pattern
	

class Match(_Pattern):
	
	def apply(self, term, context):
		match = self.pattern.match(term)
		if not match:
			raise Failure

		for name, value in match.kargs.iteritems():
			try:
				prev_value = context[name]
			except KeyError:
				context[name] = value
			else:
				if not value.isEquivalent(prev_value):
					raise Failure

		return term


class Build(_Pattern):
	
	def apply(self, term, context):
		return self.pattern.make(term, **context)
		

def Rule(match_pattern, build_pattern, **kargs):	
	return Scope(Match(match_pattern) & Build(build_pattern), **kargs)


def RuleSet(patterns, **kargs):
	rules = Fail()
	for match_pattern, build_pattern in patterns:
		rules = rules | Rule(match_pattern, build_pattern, **kargs)
	return rules

