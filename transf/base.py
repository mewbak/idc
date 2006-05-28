'''Base transformation classes.'''


# pylint: disable-msg=W0142


import aterm
import aterm.visitor


class Failure(Exception):
	'''Transformation failed to apply.'''

	# TODO: keep a reference to the failure provoking term
	
	pass


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
	
	def __call__(self, term):
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


class Adaptor(Transformation):
	'''Transformation adapter for a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def __call__(self, term):
		return self.func(term, *self.args, **self.kargs)


class Proxy(Transformation):
	'''Defers the transformation to another transformation, which does not 
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']
	
	def __init__(self, subject = None):
		Transformation.__init__(self)
		self.subject = subject
	
	def __call__(self, term):
		if self.subject is None:
			raise ValueError('subject transformation not specified')
		return self.subject(term)


from transf.combinators import Not as _Not
from transf.combinators import Choice as _Choice
from transf.combinators import Composition as _Composition