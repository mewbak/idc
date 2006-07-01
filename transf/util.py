'''Utilitary transformations.'''


from transf import exception
from transf import base


class Adaptor(base.Transformation):
	'''Transformation adapter for a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		base.Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def apply(self, term, ctx):
		return self.func(term, *self.args, **self.kargs)


class BoolAdaptor(Adaptor):
	'''Transformation adapter for a boolean function.'''
	
	def apply(self, term, ctx):
		if self.func(term, *self.args, **self.kargs):
			return term
		else:
			raise exception.Failure


class Proxy(base.Transformation):
	'''Defers the transformation to another transformation, which does not 
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']
	
	def __init__(self, subject = None):
		base.Transformation.__init__(self)
		self.subject = subject
	
	def apply(self, term, ctx):
		if self.subject is None:
			raise exception.Fatal('subject transformation not specified')
		return self.subject.apply(term, ctx)

	def __repr__(self):
		return '<%s ...>' % (self.__class__.__name__,)
