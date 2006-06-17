'''Base classes for transformations operators.'''


from transf import base


class UnaryMixin(object):
	'''Base mix-in class for unary operations on transformations.'''
	
	__slots__ = ['operand']
	
	def __init__(self, operand):
		assert isinstance(operand, base.Transformation)
		self.operand = operand


class BinaryMixin(object):
	'''Base mix-in class for binary operations on transformations.'''

	__slots__ = ['loperand', 'roperand']	
	
	def __init__(self, loperand, roperand):
		assert isinstance(loperand, base.Transformation)
		assert isinstance(roperand, base.Transformation)
		self.loperand = loperand
		self.roperand = roperand


class TernaryMixin(object):
	'''Base mix-in class for ternary operations on transformations.'''

	__slots__ = ['operand1', 'operand2', 'operand3']		
	
	def __init__(self, operand1, operand2, operand3):
		assert isinstance(operand1, base.Transformation)
		assert isinstance(operand2, base.Transformation)
		assert isinstance(operand3, base.Transformation)
		self.operand1 = operand1
		self.operand2 = operand2
		self.operand3 = operand3
	

class Unary(base.Transformation, UnaryMixin):
	'''Base class for unary operations on transformations.'''
	
	__slots__ = []
	
	def __init__(self, operand):
		base.Transformation.__init__(self)
		UnaryMixin.__init__(self, operand)


class Binary(base.Transformation, BinaryMixin):
	'''Base class for binary operations on transformations.'''

	__slots__ = []	
	
	def __init__(self, loperand, roperand):
		base.Transformation.__init__(self)
		BinaryMixin.__init__(self, loperand, roperand)


class Ternary(base.Transformation, TernaryMixin):
	'''Base class for ternary operations on transformations.'''

	__slots__ = []		
	
	def __init__(self, operand1, operand2, operand3):
		base.Transformation.__init__(self)
		TernaryMixin.__init__(self, operand1, operand2, operand3)
	

def _NaryIter(loperands_iter, Binary, roperand):
	'''Build a N-ary by the right-association of binary operators.'''
	try:
		loperand = loperands_iter.next()
	except StopIteration:
		return roperand
	else:
		return Binary(loperand, Nary(loperands_iter, Binary, roperand))

def Nary(loperands, Binary, roperand):
	'''Build a N-ary by the right-association of binary operators.'''
	return _NaryIter(iter(loperands), Binary, roperand)
