'''Transformations which introduce new scopes.'''


from transf import context
from transf.types import term
from transf import operate


class Anonymous(str):
	'''Anonymous variable name.

	This class is a string with singleton properties, i.e., it has an unique hash,
	and it is equal to no object other than itself. Instances of this class can be
	used in replacement of regular string to ensure no name collisions will ocurr,
	effectivly providing means to anonymous variables.
	'''

	__slots__ = []

	def __hash__(self):
		return id(self)

	def __eq__(self, other):
		return self is other

	def __ne__(self, other):
		return self is not other


class Scope(operate.Unary):
	'''Introduces a new variable scope before the transformation.'''

	def apply(self, term, ctx):
		ctx = context.Context([], ctx)
		return self.operand.apply(term, ctx)

	def _get_subject(self):
		return self.operand.subject
	def _set_subject(self, subject):
		self.operand.subject = subject
	subject = property(_get_subject, _set_subject)


class _Local(operate.Unary):

	def __init__(self, vars, operand):
		operate.Unary.__init__(self, operand)
		self.vars = vars

	def apply(self, term, ctx):
		vars = [(name, factory()) for name, factory in self.vars]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(term, ctx)

def Local(names, operand):
	'''Introduces a new variable scope before the transformation.'''
	vars = [(name, term.Term) for name in names]
	return _Local(vars, operand)


class _With(operate.Unary):

	def __init__(self, vars, operand):
		operate.Unary.__init__(self, operand)
		self.vars = vars

	def apply(self, term, ctx):
		vars = [(name, constructor.create(term, ctx)) for name, constructor in self.vars]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(term, ctx)


def With(vars, operand):
	if not vars:
		return operand
	return _With(vars, operand)


