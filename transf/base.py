'''Base transformation classes.'''


import aterm.factory
import aterm.terms

from transf import exception
from transf import context


class Transformation(object):
	'''Abstract class for term transformations.
	
	A transformation takes as input a term and returns the transformed term, or
	raises a failure exception if it is not applicable. It also receives a
	transformation context to which it can read/write.
	
	A transformation should B{not} maintain any state itself, i.e., different calls
	to the L{apply} method with the same term and context must produce the same
	result.
	'''
	
	__slots__ = []
	
	def __init__(self):
		'''Constructor.'''
		pass
	
	def __call__(self, trm, ctx = None):
		'''User-friendly wrapper for L{apply}.'''
		if isinstance(trm, basestring):
			trm = aterm.factory.factory.parse(trm)
		if ctx is None:
			ctx = context.empty
		return self.apply(trm, ctx)

	def apply(self, trm, ctx):
		'''Applies the transformation to the given term with the specified context.
		
		@param trm: L{Term<aterm.terms.Term>} to be transformed.
		@param ctx: Transformation L{context<context.Context>}.
		@return: The transformed term on success.
		@raise exception.Failure: on failure.
		'''
		raise NotImplementedError

	def __neg__(self):
		'''Negation operator. Shorthand for L{combine.Not}'''
		from transf import combine
		return combine.Not(self)
	
	def __pos__(self):
		'''Positive operator. Shorthand for L{combine.Try}'''
		from transf import combine
		return combine.Try(self)
	
	def __add__(self, other):
		'''Addition operator. Shorthand for L{combine.Choice}'''
		from transf import combine
		return combine.Choice(self, other)

	def __mul__(self, other):
		'''Multiplication operator. Shorthand for L{combine.Composition}'''
		from transf import combine
		return combine.Composition(self, other)	

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
	'''Identity transformation. Always returns the input term unaltered.'''
	
	def apply(self, trm, ctx):
		return trm

id = ident = Ident()


class Fail(Transformation):
	'''Failure transformation. Always raises an L{exception.Failure}.'''
	
	def apply(self, trm, ctx):
		raise exception.Failure

fail = Fail()

