'''Utilitary transformations.'''


from transf import exception
from transf import transformation


class Adaptor(transformation.Transformation):
	'''Transformation adapter for a regular function.'''

	def __init__(self, func):
		transformation.Transformation.__init__(self)
		self.func = func
		self.__doc__ = func.__doc__

	def apply(self, trm, ctx):
		trm = self.func(trm)
		if trm is None:
			raise exception.Failure
		else:
			return trm


class BoolAdaptor(Adaptor):
	'''Transformation adapter for a boolean function.'''

	def apply(self, trm, ctx):
		if self.func(trm):
			return trm
		else:
			raise exception.Failure


class MethodTransformation(transformation.Transformation):

	def __init__(self, method, obj):
		self.method = method
		self.obj = obj
		self.__doc__ = method.__doc__

	def apply(self, trm, ctx):
		return self.method(self.obj, trm, ctx)


class TransformationMethod(object):

	def __init__(self, method):
		self.method = method
		self.__doc__ = method.__doc__

	def __get__(self, obj, objtype=None):
		return MethodTransformation(self.method, obj)


class Proxy(transformation.Transformation):
	'''Defers the transformation to another transformation, which does not
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']

	def __init__(self, subject = None):
		transformation.Transformation.__init__(self)
		self.subject = subject

	def apply(self, trm, ctx):
		if self.subject is None:
			raise exception.Fatal('subject transformation not specified')
		return self.subject.apply(trm, ctx)

	def __repr__(self):
		return '<%s ...>' % (self.__class__.__name__,)

