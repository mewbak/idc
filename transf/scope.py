'''Base transformation classes.'''


from transf import exception
from transf import context
from transf import base


try:
	set
except NameError:
	from sets import ImmutableSet as set


class Scope(base.Transformation):
	'''Introduces a new variable scope before the transformation.'''
	
	def __init__(self, transf, locals = None):
		base.Transformation.__init__(self)
		self.transf = transf
		self.locals = locals
		
	def apply(self, term, ctx):
		new_ctx = context.Context(parent = ctx, locals = self.locals)
		return self.transf.apply(term, new_ctx)


class With(base.Transformation):
	
	def __init__(self, transf, **vars):
		base.Transformation.__init__(self)
		self.transf = transf
		self.vars = vars
		
	def apply(self, term, ctx):
		new_ctx = context.Context(parent=ctx, locals=self.vars.keys())
		for name, transf in self.vars.iteritems():
			new_ctx[name] = transf.apply(term, ctx)
		return self.transf.apply(term, new_ctx)


class Set(base.Transformation):

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		ctx[self.name] = term
		return term
