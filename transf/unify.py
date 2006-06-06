'''Term unifying transformations.'''


import aterm

from transf import base
from transf import combine
from transf import match
from transf import build
from transf import traverse
from transf import project
from transf import lists


def Foldr(tail, Cons, operand=None):
	if operand is None:
		operand = base.ident
	foldr = base.Proxy()
	foldr.subject \
		= match.nil & tail \
		| Cons(
			project.head & operand, 
			project.tail & foldr
		)
	return foldr


def Crush(tail, Cons, operand=None):
	return project.subterms & Foldr(tail, Cons, operand)


def CollectAll(operand, Union=None):
	'''Collect all subterms for which operand succeeds.
	
	@param union: transformation factory which takes two lists are produces a single one
	'''
	if Union is None:
		Union = lists.Concat
	collect = base.Proxy()
	crush = Crush(build.nil, Union, collect)
	collect.subject \
		= build.Cons(operand, crush) \
		| crush
	return collect