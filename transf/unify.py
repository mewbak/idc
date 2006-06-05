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
		operand = base.ident
	foldr = base.Proxy()
	foldr.subject \
		= match.nil & tail \
		| build.List((
			project.head & operand, 
			project.tail & foldr
		)) & cons
	return foldr


def Crush(tail, cons, operand=None):
	return project.subterms & Foldr(tail, cons, operand)


def CollectAll(operand, union=None):
	'''Collect all subterms for which operand succeeds.
	
	@param union: transformation which takes two lists are produces a single one
	'''
	if union is None:
		union = lists.Concat(project.first, project.second)
	collect = base.Proxy()
	crush = Crush(build.nil, union, collect)
	collect.subject \
		= build.Cons(operand, crush) \
		| crush
	return collect