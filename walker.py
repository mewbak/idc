

import aterm


class TransformationFailureException(Exception):
	
	pass


class Walker:

	def __init__(self, factory):
		self.factory = factory

	def __apply__(self, term):
		raise NotImplementedError
