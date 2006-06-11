'''Base transformation classes.'''


from transf import exception
from transf import context
from transf import combine
from transf import base


try:
	set
except NameError:
	from sets import ImmutableSet as set


class Local(combine.Unary):
	'''Introduces a new variable scope before the transformation.'''
	
	def __init__(self, operand, names = None):
		combine.Unary.__init__(self, operand)
		self.names = names
		
	def apply(self, term, ctx):
		ctx = context.Context(self.names, ctx)
		return self.operand.apply(term, ctx)


class Let(combine.Unary):
	
	def __init__(self, operand, **vars):
		combine.Unary.__init__(self, operand)
		self.vars = vars
		
	def apply(self, term, ctx):
		new_ctx = context.Context(self.vars.keys(), ctx)
		for name, transf in self.vars.iteritems():
			new_ctx[name] = transf.apply(term, ctx)
		return self.operand.apply(term, new_ctx)


class Set(base.Transformation):

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		ctx[self.name] = term
		return term
