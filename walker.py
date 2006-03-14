

import aterm


class Failure(Exception):
	
	pass


class Walker:

	def __init__(self, factory):
		self.factory = factory

	def __apply__(self, root):
		raise NotImplementedError
		
	def map(self, target, func, *args):
		if target.getType() != aterm.LIST:
			raise Failure

		if target.isEmpty():
			return target

		return self.factory.makeConsList(
				func(target.getHead(), *args), 
				self.map(target.getTail(), func, *args)
			)
		
