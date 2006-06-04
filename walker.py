'''Base classes for term walker construction.

A walker is a class aimed to process/transform a aterm as it traverses the tree.

An aterm walker's interface is very liberal: is up to the caller determine which
method to call and which arguments to pass, and the return is not necessarily an
aterm. Nevertheless, it is usually expected that the first argument is the
target term, and that a Failure exception can be raised if the transformation is
not successful.

As a walker may change its context as it traverses the tree, sucessive calls to
the same walker method's do not necessarily yield the same results.
'''


import sys

import aterm

from transf import Failure


class Walker:
	'''Aterm walker base class.'''

	def __init__(self, factory):
		# TODO: eliminate this
		self.factory = factory
	
	#def __call__(self, root):
	#	'''Apply this walker transformation to the root aterm.  Since a walker may
	#	store context, this method should be called only once in the object's
	#	lifetime. May not be implemented for every walkers.'''
	#	
	#	raise NotImplementedError

	def _match(self, term, pattern):
		match = term.rmatch(pattern)
		if match:
			caller = sys._getframe(1)
			caller.f_locals.update(match.kargs)
			return True
		else:
			return False
	
	def _dispatchAppl(self, term, methodPrefix, **kargs):
		if term.type != aterm.types.APPL:
			raise ValueError('not an application term', term)
		name = term.name
		if name.type != aterm.types.STR:
			raise ValueError('name not a string term', name)
		methodName = methodPrefix + name.value
		try:
			method = getattr(self, methodName)
		except AttributeError:
			raise ValueError('unexpected name', name)
		args = term.args
		return method(*args, **kargs)
	
	def _fail(self, target, msg = None):
		'''Signals a transformation failure, with an optional error message.'''
		if msg is None:
			msg = 'failed to transform term'
		else:
			msg = msg.getValue()
		msg = '%s: %r' % (msg, target)
		raise Failure(msg, target)
	
	def _assertFail(self, target, msg = None):
		'''Signals an assertion failure, with an optional error message.'''
		if msg is None:
			msg = 'unexpected term'
		else:
			msg = msg.getValue()
		msg = '%s: %r' % (msg, target)
		raise AssertionError(msg)
	
	def _int(self, target):
		'''Enforce the target is an integer term.'''
		if target.getType() != aterm.types.INT:
			raise Failure("not an integer term", target)
		return target
	
	def _real(self, target):
		'''Enforce the target is a real term.'''
		if target.getType() != aterm.types.REAL:
			raise Failure("not a real term", target)
		return target
	
	def _str(self, target):
		'''Enforce the target is a string term.'''
		if target.getType() != aterm.types.STR:
			raise Failure("not a string term", target)
		return target
	
	def _lit(self, target):
		'''Enforce the target to be a literal term.'''
		if not target.getType() in (aterm.types.INT, aterm.types.REAL, aterm.types.STR):
			raise Failure("not a literal term", target)
		return target
	
	def _list(self, target):
		'''Enforce the target is a list term.'''
		if target.getType() != aterm.types.LIST:
			raise Failure("not a list term", target)
		return target
	
	def _appl(self, target):
		'''Enforce the target is an application term.'''
		if target.getType() != aterm.types.APPL:
			raise Failure("not an application term", target)
		return target
	
	def _map(self, target, func, *args, **kargs):
		'''Applies the given function to every element in the target. The target must be
		a list, and the result will also be a list.'''
		if target.getType() != aterm.types.LIST:
			raise TypeError('not a list term: %r' % target)
		if target.isEmpty():
			return target
		return target.factory.makeCons(
				func(target.getHead(), *args), 
				self._map(target.getTail(), func, *args, **kargs),
				target.getAnnotations()
			)

	def _cat(self, target, tail):
		'''Concatenates two lists.'''
		if target.getType() != aterm.types.LIST:
			raise TypeError('not a list term: %r' % target)
		if target.isEmpty():
			return tail
		return target.factory.makeCons(
				target.getHead(), 
				self._cat(target.getTail(), tail),
				target.getAnnotations()
			)

	def _catMany(self, target):
		'''Concatenates several lists.'''
		if target.getType() != aterm.types.LIST:
			raise TypeError('not a list term: %r' % target)
		if target.isEmpty():
			return target		
		return self._cat(
				target.getHead(),
				self._catMany(target.getTail())
			)
	
