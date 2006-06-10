'''Base transformation classes.'''


from transf import exception
from transf import context as _context
from transf import base


class Scope(base.Transformation):
	'''Introduces a new variable scope before the transformation.'''
	
	def __init__(self, transf, locals = None):
		base.Transformation.__init__(self)
		self.transf = transf
		self.locals = locals
		
	def apply(self, term, context):
		new_context = _context.Context(parent=context, locals=self.locals)
		return self.transf(term, new_context)


class With(base.Transformation):
	
	def __init__(self, transf, **vars):
		base.Transformation.__init__(self)
		self.transf = transf
		self.vars = vars
		
	def apply(self, term, context):
		new_context = _context.Context(parent=context, locals=self.vars.keys())
		for name, transf in self.vars.iteritems():
			new_context[name] = transf.apply(term, context)
		return self.transf(term, new_context)


class Set(base.Transformation):

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, context):
		context[self.name] = term
		return term
