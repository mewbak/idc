'''Transformations which introduce new scopes.'''


from transf import exception
from transf import context
from transf import base
from transf import _operate


try:
	set
except NameError:
	from sets import ImmutableSet as set


class Local(_operate.Unary):
	'''Introduces a new variable scope before the transformation.'''
	
	def __init__(self, operand, names = None):
		_operate.Unary.__init__(self, operand)
		self.names = names
		
	def apply(self, term, ctx):
		ctx = context.Context(self.names, ctx)
		return self.operand.apply(term, ctx)


class Let(_operate.Unary):
	
	def __init__(self, operand, **vars):
		_operate.Unary.__init__(self, operand)
		self.vars = vars
		
	def apply(self, term, ctx):
		new_ctx = context.Context(self.vars.keys(), ctx)
		for name, transf in self.vars.iteritems():
			new_ctx[name] = transf.apply(term, ctx)
		return self.operand.apply(term, new_ctx)


class Set(base.Transformation):
	
	# XXX: move this away

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		ctx[self.name] = term
		return term
