'''Term rewriting transformations.'''


# pylint: disable-msg=W0142


import aterm
import aterm.visitor

from transf.base import *


# TODO: pre-parse the patterns


class Match(Transformation):
	
	def __init__(self, pattern, **kargs):
		self.pattern = pattern
		self.kargs = kargs

	def __call__(self, term):
		factory = term.factory
		args = []
		kargs = self.kargs.copy()
		if factory.match(self.pattern, term, args, kargs):
			return term
		else:
			raise Failure	


class Rule(Transformation):
	
	def __init__(self, match_pattern, build_pattern, **kargs):
		factory = aterm.Factory()
		if isinstance(match_pattern, basestring):
			match_pattern = factory.parse(match_pattern)
		if isinstance(build_pattern, basestring):
			build_pattern = factory.parse(build_pattern)
			
		self.match_pattern = match_pattern
		self.build_pattern = build_pattern
		self.kargs = kargs
	
	def __call__(self, term):
		factory = term.factory
		args = []
		kargs = self.kargs.copy()
		if self.match_pattern.match(term, args, kargs):
			return self.build_pattern.make(*args, **kargs)
		else:
			raise Failure


# TODO: write a MatchSet, BuildSet, RuleSet

