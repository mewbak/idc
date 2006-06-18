'''Context variables.'''


from transf import exception
from transf import base


class Variable(object):
	'''Base class for context variables.
	
	Although this class defines the interface of some basic and common variable
	operations, the actual semantics of these operations are specific to each of
	the derived class. Derived classes are also free to provide more variable
	operations, and the corresponding transformations.
	'''
	
	__slots__ = []
	
	def __init__(self):
		pass
	
	def match(self, term):
		'''Match the term against this variable.
		Used by L{transf.match.Var}.
		'''
		raise exception.Failure('unsupported operation')
	
	def build(self):
		'''Builds the variable.
		Used by L{transf.build.Var}.
		'''
		raise exception.Failure('unsupported operation')
	
	def traverse(self, term):
		'''Traverse the variable.
		Used by L{transf.traverse.Var}.
		'''
		raise exception.Failure('unsupported operation')
		

# TODO: define a factory?
	

class Term(Variable):
	'''Term variable.'''
	
	__slots__ = ['term']
	
	def __init__(self, term = None):
		Variable.__init__(self)
		self.term = term
	
	def match(self, term):
		'''Match the term against this variable value, setting it,
		if it is undefined.'''
		if self.term is None:
			self.term = term
		elif self.term == term:
			return term
		else:
			raise exception.Failure('variable mismatch', term, self.term)
	
	def build(self):
		'''Returns this variable term, if defined.'''
		if self.term is None:
			raise exception.Failure('undefined variable')
		else:
			return self.term

	def traverse(self, term):
		'''Resets this variable value.'''
		self.term = term
		return term
		
	def __repr__(self):
		return '<%s.%s %r>' % (__name__, self.__class__.__name__, self.term)


class Transformation(base.Transformation):
	'''Base class for variable transformations.'''
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	

class Wrap(Transformation):
	'''Variable operation wrapper.
	
	This is an utility class which uses Python's instrospective abilities to easily 
	wrap variable operations as transformations.
	'''
	
	def __init__(self, name, method, *operands):
		'''Creates a new variable wrapper.
		
		@param name: variable name
		@param method: name of variable method to be called
		@param operands: operand transformations whose result will be passed to the 
		operation
		'''
		Transformation.__init__(self, name)
		self.method = method
		self.operands = operands
	
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		try:
			method = getattr(var, self.method)
		except AttributeError:
			raise exception.Fatal('unsupported operation', var, self.method)
		args = [operand.apply(term, ctx) for operand in self.operands] + [term]
		print method, args
		res = method(*args)
		if res is None:
			return term
		return res
