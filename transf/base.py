'''Base transformation classes.'''


import aterm.terms
import aterm.factory

from transf import exception
from transf import context


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
	
	def __call__(self, term, ctx = None):
		'''User-friendly wrapper for apply.'''
		if isinstance(term, basestring):
			term = _factory.parse(term)
		if ctx is None:
			ctx = context.empty
		return self.apply(term, ctx)

	def apply(self, term, ctx):
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
		name = self.__class__.__module__ + '.' + self.__class__.__name__
		attrs = {}
		for objname in dir(self):
			obj = getattr(self, objname)
			if isinstance(obj, (Transformation, aterm.terms.Term)):
				try:
					objrepr = repr(obj)
				except:
					objrepr = "<error>"
				attrs[objname] = objrepr
		return '<' + name + '(' + ', '.join(["%s=%s" % attr for attr in attrs.iteritems()]) + ')>'
			

class Ident(Transformation):
	'''Identity transformation.'''
	
	def apply(self, term, ctx):
		return term

id = ident = Ident()


class Fail(Transformation):
	'''Failure transformation.'''
	
	def apply(self, term, ctx):
		raise exception.Failure

fail = Fail()


class Adaptor(Transformation):
	'''Transformation adapter for a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def apply(self, term, ctx):
		return self.func(term, ctx, *self.args, **self.kargs)


class Proxy(Transformation):
	'''Defers the transformation to another transformation, which does not 
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']
	
	def __init__(self, subject = None):
		Transformation.__init__(self)
		self.subject = subject
	
	def apply(self, term, ctx):
		if self.subject is None:
			raise ValueError('subject transformation not specified')
		return self.subject.apply(term, ctx)

	def __repr__(self):
		return '<%s ...>' % (self.__class__.__name__,)


def Rec(Def):
	'''Recursive transformation.
	
	@param Def: transformation factory whose single argument is its own definition.
	'''
	rec = Proxy()
	rec.subject = Def(rec)
	return rec
