

class TransformationFailureException(Exception):
	
	pass


class Transformation:
	
	def __apply__(self, target):
		return self.apply(target)

	def apply(self, target):
		raise NotImplementedError

	def __not__(self):
		return Not(self)
	
	def __or__(self, other):
		return Or(self, other)

	def __and__(self, other):
		return And(self, other)


class Identity(Transformation):
	
	def apply(self, target):
		return target


class Fail(Transformation):
	
	def apply(self, target):
		raise TransformationFailureException


class ContextTransformation(Transformation):
	
	def __init__(self, context):
		self.context


class ResetContext(ContextTransformation):
	
	def apply(self, target):
		self.context = {}
		return target


class Match(ContextTransformation):

	def __init__(self, pattern, context):
		ContextTransformation.__init__(self, context)
		self.pattern = pattern
	
	def apply(self, target):
		if not self.pattern.match(target, kargs=self.context):
			raise FailTransformation
		else:
			return target


class Build(Transformation):
	
	def __init__(self, pattern, context):
		ContextTransformation.__init__(self, context)
		self.pattern = pattern
	
	def apply(self, target):
		return self.pattern.make(**self.context)


class UnaryOp(Transformation):
	
	def __init__(self, operand):
		self.operand = operand


class Not(UnaryOp):
	
	def apply(self, target):
		try:
			self.operand.apply(target)
		except TransformationFailureException:
			return target
		
		raise TransformationFailureException


class BinaryOp(Transformation):
	
	def __init__(self, loperand, roperand):
		self.loperand = loperand
		self.roperand = roperand


class Or(Transformation):
	
	def apply(self, target):
		try:
			return self.loperand.apply(target)
		except TransformationFailureException:
			return self.roperand.apply(target)


class And(Transformation):
	
	def apply(self, target):
		result = self.loperand.apply(target)
		return self.roperand.apply(result)


def Rule(match_pattern, build_pattern):
	context = {}
	return \
		ResetContext(context) \
		& Match(match_pattern, context) \
		& Build(build_pattern, context)
