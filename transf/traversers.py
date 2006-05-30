'''Term traversing transformations.'''


# pylint: disable-msg=W0142


import aterm

from transf.base import *
from transf.combinators import *
from transf.term import *


def Map(operand):
	map = Proxy()
	map.subject = Nil() | Cons(operand, map)
	return map


def Fetch(operand):
	fetch = Proxy()
	fetch.subject = Cons(operand, Ident()) | Cons(Ident(), fetch)
	return fetch


def Filter(operand):
	filter = Proxy()
	filter.subject = Nil() | ConsFilter(operand, filter)
	return filter


class All(Unary):
	'''Applies a transformation to all subterms of a term.'''
	
	def __init__(self, operand):
		Unary.__init__(self, operand)
		self.list_transf = Map(operand)
		self.appl_transf = Appl(Ident(), self.list_transf)
	
	def apply(self, term, context):
		if term.type == aterm.types.APPL:
			return self.appl_transf(term, context)
		elif term.type == aterm.types.LIST:
			return self.list_transf(term, context)
		else:
			return term


def BottomUp(operand):
	bottomup = Proxy()
	bottomup.subject = All(bottomup) & operand
	return bottomup


def TopDown(operand):
	topdown = Proxy()
	topdown.subject = operand & All(topdown)
	return topdown


def InnerMost(operand):
	innermost = Proxy()
	innermost.subject = BottomUp(Try(operand & innermost))
	return innermost
