'''Base transformation classes.'''


import aterm.terms
import aterm.factory

from transf import exception
from transf import context as _context


_factory = aterm.factory.Factory()


class Transformation(object):
	'''Base class for transformations. 
	
	A transformation takes as input a term and returns the transformed term, or
	raises a failure exception if it is not applicable.
	
	Albeit convenient, it is not necessary for every transformation to derive from
	this class. Generally, a regular function can be used instead.
	'''
	
	__slots__ = []
	
	def __init__(self):
		pass
	
	def __call__(self, term, context = None):
		'''Applies the transformation.'''
		if isinstance(term, basestring):
			term = _factory.parse(term)
		if context is None:
			context = _context.Context()
		return self.apply(term, context)

	def apply(self, term, context):
		'''Applies the transformation.'''
		raise NotImplementedError(self)

	def __invert__(self):
		from transf import combine
		return combine.Not(self)
	
	def __or__(self, other):
		from transf import combine
		return combine.Choice(self, other)

	def __ror__(self, other):
		from transf import combine
		return combine.Choice(other, self)

	def __and__(self, other):
		from transf import combine
		return combine.Composition(self, other)	

	def __rand__(self, other):
		from transf import combine
		return combine.Composition(other, self)
	
	def __repr__(self):
		name = self.__class__.__name__
		attrs = {}
		for objname in dir(self):
			obj = getattr(self, objname)
			if isinstance(obj, (Transformation, aterm.terms.Term)):
				try:
					objrepr = repr(obj)
				except:
					objrepr = "<error>"
				attrs[objname] = objrepr
		return name + '(' + ', '.join(["%s=%s" % attr for attr in attrs.iteritems()]) + ')'
			

class Ident(Transformation):
	'''Identity transformation.'''
	
	def apply(self, term, context):
		return term

ident = Ident()


class Fail(Transformation):
	'''Failure transformation.'''
	
	def apply(self, term, context):
		raise exception.Failure

fail = Fail()


class Adaptor(Transformation):
	'''Transformation adapter for a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def apply(self, term, context):
		return self.func(term, context, *self.args, **self.kargs)


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



