'''Base transformation classes.'''


from transf.exception import Failure


class Transformation(object):
	'''Base class for transformations. 
	
	A transformation takes as input a term and returns the transformed term, or
	raises a Failure exception if it is not applicable.
	
	Albeit convenient, it is not necessary for every transformation to derive from
	this class. Generally, a regular function can be used instead.
	'''
	
	__slots__ = []
	
	def __init__(self):
		pass
	
	def __call__(self, term, context = None):
		'''Applies the transformation.'''
		if context is None:
			context = {}
		return self.apply(term, context)

	def apply(self, term, context):
		'''Applies the transformation.'''
		raise NotImplementedError

	def __not__(self):
		return _Not(self)
	
	def __or__(self, other):
		return _Choice(self, other)

	def __ror__(self, other):
		return _Choice(other, self)

	def __and__(self, other):
		return _Composition(self, other)	

	def __rand__(self, other):
		return _Composition(other, self)


class Scope(Transformation):
	'''Introduces a new variable scope before the transformation.'''
	
	def __init__(self, transf, **kargs):
		Transformation.__init__(self)
		self.transf = transf
		self.kargs = kargs
		
	def apply(self, term, context):
		context = self.kargs.copy()
		return self.transf(term, context)


class Adaptor(Transformation):
	'''Transformation adapter for a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def apply(self, term, context):
		return self.func(term, *self.args, **self.kargs)


class Proxy(Transformation):
	'''Defers the transformation to another transformation, which does not 
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']
	
	def __init__(self, subject = None):
		Transformation.__init__(self)
		self.subject = subject
	
	def apply(self, term, context):
		if self.subject is None:
			raise ValueError('subject transformation not specified')
		return self.subject(term, context)


from transf.combinators import Not as _Not
from transf.combinators import Choice as _Choice
from transf.combinators import Composition as _Composition