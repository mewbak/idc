

import aterm


class TransformationFailure(Exception):
	
	pass


class Transformation:

	def apply(self, term, context):
		raise NotImplementedError


class Identity(Transformation):
	
	def apply(self, term, context):
		return term


class Fail(Transformation):
	
	def apply(self, term, context):
		raise TransformationFailure


class Match(Transformation):

	def __init__(self, pattern):
		self.pattern = pattern
	
	def apply(self, term, context):
		if not self.pattern.match(term, kargs=context):
			raise FailTransformation
		else:
			return term


class Build(Transformation):
	
	def __init__(self, pattern):
		self.pattern = pattern
		
	def apply(self, term, context):
		self.pattern.make(kargs=context)



