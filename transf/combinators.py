'''Transformation combinators.'''


# pylint: disable-msg=W0142


import aterm
import aterm.visitor

from transf.base import *


class Ident(Transformation):
	'''Identity transformation.'''
	
	def __call__(self, term):
		return term
	

class Fail(Transformation):
	'''Failure transformation.'''
	
	def __call__(self, term):
		raise Failure


class Unary(Transformation):
	'''Base class for unary operations on transformations.'''
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.operand = operand


class Not(Unary):
	'''Fail if a transformation applies.'''
	
	def __call__(self, term):
		try:
			self.operand(term)
		except Failure:
			return term
		else:
			raise Failure


class Try(Unary):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	def __call__(self, term):
		try:
			return self.operand(term)
		except Failure:
			return term


class Where(Unary):
	'''Succeeds if the transformation succeeds, but returns the original 
	term.
	'''
	
	def __call__(self, term):
		self.operand(term)
		return term


class Binary(Transformation):
	'''Base class for binary operations on transformations.'''
	
	def __init__(self, loperand, roperand):
		Transformation.__init__(self)
		self.loperand = loperand
		self.roperand = roperand


class Choice(Binary):
	'''Attempt the first transformation, transforming the second on failure.'''
	
	def __call__(self, term):
		try:
			return self.loperand(term)
		except Failure:
			return self.roperand(term)


class Composition(Binary):
	'''Transformation composition.'''
	
	def __call__(self, term):
		return self.roperand(self.loperand(term))


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = Proxy()
	repeat.subject = Try(operand & repeat)
	return repeat
