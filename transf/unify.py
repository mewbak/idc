'''Term unifying transformations.'''


from transf import base
from transf import util
from transf import combine
from transf import match
from transf import build
from transf import project
from transf import arith


def Foldr(tail, Cons, operand=None):
	if operand is None:
		operand = base.ident
	foldr = util.Proxy()
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


def Crush(tail, Cons, operand = None):
	return project.subterms & Foldr(tail, Cons, operand)


def CollectAll(operand, Union = None, reduce = None):
	'''Collect all subterms for which operand succeeds.
	
	collect all subterms with user-defined union operator and
	a skip argument.
	
	@param Union: transformation factory which takes two lists and produces a
	single one and produce a single one.
	If duplicates must be removed, then this argument should be union,
	otherwise it defaults to concat.

	@param reduce: it can be used to reduce the current term before
	collecting subterms of it. Producing the empty list will result
	in a complete skip of all subterms.
	'''
	if Union is None:
		from transf.lists import Concat as Union
	collect = util.Proxy()
	crush = Crush(build.nil, Union, collect)
	if reduce is not None:
		crush = combine.Try(reduce) & crush
	collect.subject = build.Cons(operand, crush) | crush
	#else:
		#collect.subject = build.Cons(operand, crush) | reduce & collect | crush
		#collect.subject = build.Cons(operand, crush) | combine.Try(reduce) & crush
	return collect


def CountAll(operand):
	'''Count the number of occorrences in all subterms.'''
	count = util.Proxy()
	count.subject = arith.AddInt(
		_CountOne(operand), 
		Crush(
			build.zero,
			arith.AddInt,
			count
		)
	)

