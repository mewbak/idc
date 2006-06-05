'''Term unifying transformations.'''


import aterm

from transf import base
from transf import combine
from transf import match
from transf import build
from transf import project
from transf import lists


def Foldr(tail, cons, operand=None):
	if operand is None:
		operand = combine.Ident()
	foldr = base.Proxy()
	foldr.subject \
		= match.MatchNil() & tail \
		| build.BuildList((
			project.Head() & operand, 
			project.Tail() & foldr
		)) & cons
	return foldr


def Crush(tail, cons, operand=None):
	return project.SubTerms() & Foldr(tail, cons, operand)


def CollectAll(operand, union=None):
	'''Collect all subterms for which operand succeeds.
	
	@param union: transformation which takes two lists are produces a single one
	'''
	if union is None:
		union = lists.Concat(project.First(), project.Second())
	collect = base.Proxy()
	crush = Crush(build.BuildNil(), union, collect)
	collect.subject \
		= build.BuildCons(operand, crush) \
		| crush
	return collect