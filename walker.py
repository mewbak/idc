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

import sys


class Failure(Exception):
	'''Failure to transform a term.'''
	
	def __init__(self, msg = None, *args):
		Exception.__init__(self, *args)
		self.msg = msg
	
	def __str__(self):
		if self.msg is None:
			return Exception.__str(self)
		else:
			if len(self.args):
				return self.msg % self.args
			else:
				return self.msg

# TODO: create/use another exception for fatal/assertion errors


class Walker:
	'''Aterm walker base class.'''

	def __init__(self, factory):
		self.factory = factory
		self._setup()
	
	def _setup(self):
		'''Called by the constructor method after setting the factory attribute to
		perform initial setup. It may be used, for example, parse/make aterm
		patterns.'''

		pass

	#def __apply__(self, root):
	#	'''Apply this walker transformation to the root aterm.  Since a walker may
	#	store context, this method should be called only once in the object's
	#	lifetime. May not be implemented for every walkers.'''
	#	
	#	raise NotImplementedError

	def _fail(self, target, msg = None, fatal = False):
		if msg is None:
			msg = "failed to transform '%r'"
		else:
			self._str(msg)
			msg = msg.getValue().replace('%', '%%') + ": '%r'"
		if fatal:
			sys.stderr.write(msg % target + '\n')
		raise Failure(msg, target)
	
	def _fatal(self, target, msg = None):
		self._fail(target, msg, True)
	
	def _int(self, target):
		'''Enforce the target is an integer term.'''
		if target.getType() != aterm.INT:
			raise Failure("'%r' is not an integer term", target)
		return target
	
	def _real(self, target):
		'''Enforce the target is a real term.'''
		if target.getType() != aterm.REAL:
			raise Failure("'%r' is not a real term", target)
		return target
	
	def _str(self, target):
		'''Enforce the target is a string term.'''
		if target.getType() != aterm.STR:
			raise Failure("'%r' is not a string term", target)
		return target
	
	def _lit(self, target):
		'''Enforce the target to be a literal term.'''
		if not target.getType() in (aterm.INT, aterm.REAL, aterm.STR):
			raise Failure("'%r' is not a literal term", target)
		return target
	
	def _list(self, target):
		'''Enforce the target is a list term.'''
		if target.getType() != aterm.LIST:
			raise Failure("'%r' is not a list term", target)
		return target
	
	def _appl(self, target):
		'''Enforce the target is an application term.'''
		if target.getType() != aterm.APPL:
			raise Failure("'%r' is not an application term", target)
		return target
	
	def _map(self, target, func, *args, **kargs):
		'''Applies the given function to every element in the target. The target must be
		a list, and the result will also be a list.'''
		
		self._list(target)

		if target.isEmpty():
			return target
		
		return self.factory.makeConsList(
				func(target.getHead(), *args), 
				self._map(target.getTail(), func, *args, **kargs)
			)

	def _cat(self, *args):
		'''Concatenates several lists.'''
		
		if len(args) == 0:
			return self.factory.makeNilList()
		if len(args) == 1:
			self._list(args[0])
			return args[0]
		return self._cat2(args[0], self._cat(*args[1:]))
	
	def _cat2(self, x, y):
		'''Concatenates two lists.'''
		self._list(x)
		if x.isEmpty():
			self._list(y)
			return y
		return self.factory.makeConsList(
				x.getHead(), 
				self._cat(x.getTail(), y)
			)

