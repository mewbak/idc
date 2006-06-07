'''Term unifying transformations.'''


import aterm

from transf import base
from transf import combine
from transf import match
from transf import build
from transf import traverse
from transf import project
#from transf import lists
from transf import arith


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


def _CountOne(operand):
	return combine.GuardedChoice(operand, build.one, build.zero)


def Count(operand):
	'''Count the number of occorrences in a list.'''
	return Foldr(
		build.zero, 
		arith.AddInt,
		_CountOne(operand)
	)


def Crush(tail, Cons, operand=None):
	return project.subterms & Foldr(tail, Cons, operand)


def CollectAll(operand, Union=None):
	'''Collect all subterms for which operand succeeds.
	
	@param Union: transformation factory which takes two lists and produces a
	single one
	'''
	if Union is None:
		from transf.lists import Concat as Union
	collect = base.Proxy()
	crush = Crush(build.nil, Union, collect)
	collect.subject \
		= build.Cons(operand, crush) \
		| crush
	return collect


def CountAll(operand):
	'''Count the number of occorrences in all subterms.'''
	count = base.Proxy()
	count.subject = arith.AddInt(
		_CountOne(operand), 
		Crush(
			build.zero,
			arith.AddInt,
			count
		)
	)

