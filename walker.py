'''Base classes for aterm walker construction.

An aterm walker is a class aimed to transform an aterm as it traverses the tree.

An aterm walker's interface is very liberal: is up to the caller determine
which method to call and which arguments to pass, and the return is not
necessarily an aterm. Nevertheless, it is usually expected that the first
argument is the target term, and that a Failure exception can be raised if the
transformation does not succeed.

An aterm walker may store context as it traverses the tree, therefore sucessive
calls to the same walker method's do not necessarily yield the same results.
However, it is usually expected that first call after setting up a walker will.
'''


import aterm


class Failure(Exception):
	'''Failure to transform a term.'''
	
	pass


class Walker:
	'''Aterm walker base class.'''

	def __init__(self, factory):
		self.factory = factory
		self.setup()
	
	def setup(self):
		'''Called by the constructor method after setting the factory attribute to
		perform initial setup. It may be used, for example, parse/make aterm
		patterns.'''

		pass

	def __apply__(self, root):
		'''Apply this walker transformation to the root aterm.  Since a walker may
		store context, this method should be called only once in the object's
		lifetime. May not be implemented for every walkers.'''
		
		raise NotImplementedError
		
	def _map(self, target, func, *args, **kargs):
		'''Applies the given function to every element in the target. The target must be
		a list, and the result will also be a list.'''
		
		if target.getType() != aterm.LIST:
			raise Failure

		if target.isEmpty():
			return target

		return self.factory.makeConsList(
				func(target.getHead(), *args), 
				self._map(target.getTail(), func, *args, **kargs)
			)
		
