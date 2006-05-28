'''Term traversing transformations.'''


# pylint: disable-msg=W0142


import aterm
import aterm.visitor

from transf.base import *
from transf.combinators import *


class Traverser(aterm.visitor.IncrementalVisitor, Unary):
	'''Base class for all term traversers.'''

	def __init__(self, operand):
		aterm.visitor.IncrementalVisitor.__init__(self)
		Unary.__init__(self, operand)
	

class Map(Traverser):
	'''Applies a transformation to all elements of a list term.'''
	
	def visitTerm(self, term):
		raise TypeError, 'list or tuple expected: %r' % term
	
	def visitNil(self, term):
		return term

	def visitHead(self, term):
		return self.operand(term)
	
	def visitTail(self, term):
		return self.visit(term)

	def visitName(self, term):
		if term.getType() != aterm.STR and term.getValue() != "":
			return self.visitTerm(term)
		else:
			return term
	
	def visitArgs(self, term):
		return self.visit(term)
		
	def visitPlaceholder(self, term):
		# placeholders are kept unmodified
		return term


class Fetch(Map):
	'''Traverses a list until it finds a element for which the transformation 
	succeeds and then stops. That element is the only one that is transformed.
	'''
	
	def visitNil(self, term):
		raise Failure('fetch reached the end of the list')
	
	def visitCons(self, term):
		old_head = term.getHead()
		old_tail = term.getTail()
		
		try:
			new_head = self.visitHead(old_head)
		except Failure:
			new_head = old_head
			new_tail = self.visitTail(old_tail)
		else:
			new_tail = old_tail
			
		if new_head is not old_head or new_tail is not old_tail:
			annos = term.getAnnotations()
			return term.factory.makeCons(new_head, new_tail, annos)
		else:
			return term


class Filter(Map):
	'''Applies a transformation to each element of a list, keeping only the 
	elements for which it succeeds.
	'''

	def visitCons(self, term):
		old_head = term.getHead()
		old_tail = term.getTail()
		new_tail = self.visitTail(old_tail)
		
		try:
			new_head = self.visitHead(old_head)
		except Failure:
			return new_tail
			
		if new_head is not old_head or new_tail is not old_tail:
			annos = term.getAnnotations()
			return term.factory.makeCons(new_head, new_tail, annos)
		else:
			return term


class All(Map):
	'''Applies a transformation to all subterms of a term.'''

	def visitTerm(self, term):
		# terms other than applications are kept unmodified
		return term

	def visitName(self, term):
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
