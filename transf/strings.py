'''String manipulation transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import operate
from transf import combine
from transf import build
from transf import unify


class ToStr(base.Transformation):
	
	def apply(self, term, ctx):
		try:
			return term.factory.makeStr(str(term.value))
		except AttributeError:
			raise exception.Failure('not a literal term', term)


class _Concat2(operate.Binary):
	
	def apply(self, term, ctx):
		head = self.loperand.apply(term, ctx)
		tail = self.roperand.apply(term, ctx)
		if head.type != aterm.types.STR:
			raise exception.Failure('not string term', head)
		if tail.type != aterm.types.STR:
			raise exception.Failure('not string term', tail)
		return term.factory.makeStr(head.value + tail.value)

def Concat2(loperand, roperand):
	'''Concatenates two lists.'''
	if loperand is build.empty:
		return roperand
	if roperand is build.empty:
		return loperand
	return _Concat2(loperand, roperand)

concat = unify.Foldr(build.empty, Concat2)
