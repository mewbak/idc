'''Context variables.'''


from transf import exception
from transf import transformation


class Variable(object):
	'''Base class for context variables.

	Although this class defines the interface of some basic and common variable
	operations, the semantics of some of these operations are ocasionally specific
	to each of the derived class. Derived classes are also free to provide more
	variable operations, and the corresponding transformations.
	'''

	__slots__ = []

	def __init__(self):
		pass

	def set(self, term):
		'''Assign the term to this variable.

		@return: None.
		'''
		raise exception.Fatal('unsupported operation')

	def unset(self):
		'''Clear this variable.

		@return: None.
		'''
		raise exception.Fatal('unsupported operation')

	def match(self, term):
		'''Match the term against this variable.

		@return: None. An exception is raised on failure.

		Used by L{transf.lib.match.Var}.
		'''
		raise exception.Fatal('unsupported operation')

	def build(self):
		'''Builds the variable.
		Used by L{transf.build.Var}.
		'''
		raise exception.Fatal('unsupported operation')

	def traverse(self, term):
		'''Traverse the variable -- a combination of matching and building.
		Used by L{transf.congruent.Var}.
		'''
		raise exception.Fatal('unsupported operation')


class Constructor(object):
	'''Used by L{scope.With} to instantiate variables.'''
	def __init__(self):
		pass


class Operation(transformation.Transformation):
	'''Base class for variable operations.'''

	def __init__(self, name):
		'''Create variable transformation.
		@param name: variable name.
		'''
		transformation.Transformation.__init__(self)
		self.name = name


class Set(Operation):
	'''Calls L{Variable.set}.'''
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		var.set(term)
		return term


class Unset(Operation):
	'''Calls L{Variable.unset}.'''
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		var.unset()
		return term


class Match(Operation):
	'''Calls L{Variable.match}.'''
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		var.match(term)
		return term


class Build(Operation):
	'''Calls L{Variable.build}.'''
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		return var.build()


class Traverse(Operation):
	'''Calls L{Variable.traverse}.'''
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		return var.traverse(term)


class Wrap(Operation):
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
		Operation.__init__(self, name)
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
