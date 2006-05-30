'''Term traversing transformations.'''


# pylint: disable-msg=W0142


import aterm
import aterm.visitor

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
	
	def __call__(self, term):
		if term.type == aterm.types.APPL:
			return self.appl_transf(term)
		elif term.type == aterm.types.LIST:
			return self.list_transf(term)
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


class _Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.operand = operand

	def visitTerm(self, term):
		raise TypeError('not a term list: %r' % term)
	
	def visitNil(self, term):
		raise Failure
		
	def visitCons(self, term):
		try:
			head = self.operand(term.head)
		except Failure:
			head, body, tail = self.visit(term.tail)
			return head.insert(0, term.head), body, tail
		else:
			return term.factory.makeNil(), term.head, term.tail


class Split(Transformation):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.splitter = _Splitter(operand)

	def __call__(self, term):
		return term.factory.makeList(self.splitter.visit(term))


