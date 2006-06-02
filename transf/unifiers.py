'''Term unifying transformations.'''


import aterm

from transf import base
from transf import combinators
from transf import matching
from transf import building
from transf import projection
from transf import lists


def Foldr(tail, cons, operand=None):
	if operand is None:
		operand = combinators.Ident()
	foldr = base.Proxy()
	foldr.subject \
		= matching.MatchNil() & tail \
		| building.BuildList((
			projection.Head() & operand, 
			projection.Tail() & foldr
		)) & cons
	return foldr


def Crush(tail, cons, operand=None):
	return projection.SubTerms() & Foldr(tail, cons, operand)


def CollectAll(operand, union=None):
	'''Collect all subterms for which operand succeeds.
	
	@param union: transformation which takes two lists are produces a single one
	'''
	if union is None:
		union = lists.Concat(projection.First(), projection.Second())
	collect = base.Proxy()
	crush = Crush(building.BuildNil(), union, collect)
	collect.subject \
		= building.BuildCons(operand, crush) \
		| crush
	return collect