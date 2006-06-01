'''Transformation combinators.'''


from transf.base import *


class Ident(Transformation):
	'''Identity transformation.'''
	
	def apply(self, term, context):
		return term
	

class Fail(Transformation):
	'''Failure transformation.'''
	
	def apply(self, term, context):
		raise Failure


class Unary(Transformation):
	'''Base class for unary operations on transformations.'''
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.operand = operand


class Binary(Transformation):
	'''Base class for binary operations on transformations.'''
	
	def __init__(self, loperand, roperand):
		Transformation.__init__(self)
		self.loperand = loperand
		self.roperand = roperand


class Ternary(Transformation):
	
	def __init__(self, operand1, operand2, operand3):
		Transformation.__init__(self)
		self.operand1 = operand1
		self.operand2 = operand2
		self.operand3 = operand3
	

class Not(Unary):
	'''Fail if a transformation applies.'''
	
	def apply(self, term, context):
		try:
			self.operand(term, context)
		except Failure:
			return term
		else:
			raise Failure


class Try(Unary):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	def apply(self, term, context):
		try:
			return self.operand(term, context)
		except Failure:
			return term


class Where(Unary):
	'''Succeeds if the transformation succeeds, but returns the original 
	term.
	'''
	
	def apply(self, term, context):
		self.operand(term, context)
		return term


class Composition(Binary):
	'''Transformation composition.'''
	
	def apply(self, term, context):
		return self.roperand(self.loperand(term, context), context)


class Choice(Binary):
	'''Attempt the first transformation, transforming the second on failure.'''
	
	def apply(self, term, context):
		try:
			return self.loperand(term, context)
		except Failure:
			return self.roperand(term, context)


class GuardedChoice(Ternary):
	
	def apply(self, term, context):
		try:
			result = self.operand1(term, context)
		except Failure:
			return self.operand3(term, context)
		else:
			return self.operand2(result, context)


def IfThenElse(cond, true, false):
	return GuardedChoice(Where(cond), true, false)


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = Proxy()
	repeat.subject = Try(operand & repeat)
	return repeat
