'''Transformation combinators.'''


from transf import exception
from transf import base


class Unary(base.Transformation):
	'''Base class for unary operations on transformations.'''
	
	def __init__(self, operand):
		base.Transformation.__init__(self)
		self.operand = operand


class Binary(base.Transformation):
	'''Base class for binary operations on transformations.'''
	
	def __init__(self, loperand, roperand):
		base.Transformation.__init__(self)
		self.loperand = loperand
		self.roperand = roperand


class Ternary(base.Transformation):
	'''Base class for ternary operations on transformations.'''
	
	def __init__(self, operand1, operand2, operand3):
		base.Transformation.__init__(self)
		self.operand1 = operand1
		self.operand2 = operand2
		self.operand3 = operand3
	

class Not(Unary):
	'''Fail if a transformation applies.'''
	
	def apply(self, term, ctx):
		try:
			self.operand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			raise exception.Failure


class _Try(Unary):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	def apply(self, term, ctx):
		try:
			return self.operand.apply(term, ctx)
		except exception.Failure:
			return term


def Try(operand):
	if operand is base.ident:
		return operand
	if operand is base.fail:
		return base.ident
	return _Try(operand)


class Where(Unary):
	'''Succeeds if the transformation succeeds, but returns the original 
	term.
	'''
	
	def apply(self, term, ctx):
		self.operand.apply(term, ctx)
		return term


class _Composition(Binary):
	'''Transformation composition.'''
	
	def apply(self, term, ctx):
		term = self.loperand.apply(term, ctx)
		return self.roperand.apply(term, ctx)


def Composition(loperand, roperand):
	if loperand is base.ident:
		return roperand
	if roperand is base.ident:
		return loperand
	if loperand is base.fail:
		return loperand
	return _Composition(loperand, roperand)
	

class _Choice(Binary):
	'''Attempt the first transformation, transforming the second on failure.'''
	
	def apply(self, term, ctx):
		try:
			return self.loperand.apply(term, ctx)
		except exception.Failure:
			return self.roperand.apply(term, ctx)


def Choice(loperand, roperand):
	if loperand is base.ident:
		return loperand
	if loperand is base.fail:
		return roperand
	if roperand is base.ident:
		return Try(loperand)
	if roperand is base.fail:
		return loperand
	return _Choice(loperand, roperand)
	

class GuardedChoice(Ternary):
	
	def apply(self, term, ctx):
		try:
			term = self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)


class IfThen(Binary):
	
	def apply(self, term, ctx):
		try:
			self.loperand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			return self.roperand.apply(term, ctx)


class IfThenElse(Ternary):
	
	def apply(self, term, ctx):
		try:
			self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = base.Proxy()
	repeat.subject = Try(operand & repeat)
	return repeat
