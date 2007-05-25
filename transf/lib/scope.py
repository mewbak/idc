'''Transformations which introduce new scopes.'''


from transf import context
from transf import operate


class _Scope(operate.Unary):

	def __init__(self, vars, operand):
		operate.Unary.__init__(self, operand)
		self.vars = vars

	def apply(self, trm, ctx):
		vars = [(var.name, None) for var in self.vars]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(trm, ctx)

	# XXX: hack to enable the use of Proxy
	def _get_subject(self):
		try:
			return self.operand.subject
		except AttributeError:
			return None
	def _set_subject(self, subject):
		self.operand.subject = subject
	subject = property(_get_subject, _set_subject)


def Scope(vars, operand):
	'''Introduces a new variable scope before the transformation.'''
	if not vars:
		return operand
	return _Scope(vars, operand)


#class _With(operate.Unary):
#
#	def __init__(self, vars, operand):
#		operate.Unary.__init__(self, operand)
#		self.vars = vars
#
#	def apply(self, term, ctx):
#		vars = [(name, constructor.create(term, ctx)) for name, constructor in self.vars]
#		ctx = context.Context(vars, ctx)
#		return self.operand.apply(term, ctx)
#
#
#def With(vars, operand):
#	if not vars:
#		return operand
#	return _With(vars, operand)


