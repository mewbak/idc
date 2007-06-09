'''Term variables.'''


from transf import exception
from transf import transformation
from transf import variable
from transf.util import TransformationMethod


class Term(variable.Variable):

	@TransformationMethod
	def init(self, trm, ctx):
		ctx.set(self.name, None)
		return trm

	@TransformationMethod
	def set(self, trm, ctx):
		ctx.set(self.name, trm)
		return trm

	@TransformationMethod
	def clear(self, trm, ctx):
		ctx.set(self.name, None)
		return trm

	@TransformationMethod
	def match(self, trm, ctx):
		'''Match the term against this variable value, setting it,
		if it is undefined.'''
		old = ctx.get(self.name)
		if old is None:
			ctx.set(self.name, trm)
		elif old != trm:
			raise exception.Failure('variable mismatch', self.name, trm, old)
		return trm

	@TransformationMethod
	def build(self, trm, ctx):
		'''Returns this variable term, if defined.'''
		trm = ctx.get(self.name)
		if trm is None:
			raise exception.Failure('undefined variable', self.name)
		return trm

	congruent = match

