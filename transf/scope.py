'''Transformations which introduce new scopes.'''


from transf import context
from transf import variable
from transf import operate


class _Local(operate.Unary):
	
	def __init__(self, vars, operand):
		operate.Unary.__init__(self, operand)
		self.vars = vars
		
	def apply(self, term, ctx):
		vars = [(name, factory()) for name, factory in self.vars]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(term, ctx)


def Local(operand, names = None):
	'''Introduces a new variable scope before the transformation.'''
	if not names:
		return operand
	vars = [(name, variable.Term) for name in names]
	return _Local(vars, operand)


def Local2(vars, operand):
	if not vars:
		return operand
	return _Local(vars, operand)


class _Let(operate.Unary):
	
	def __init__(self, defs, operand):
		operate.Unary.__init__(self, operand)
		self.defs = defs
		
	def apply(self, term, ctx):
		vars = [(name, variable.Term(transf.apply(term, ctx))) for name, transf in self.defs]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(term, ctx)

def Let(operand, **defs):
	if not defs:
		return operand
	return _Let(defs.items(), operand)

def Let2(defs, operand):
	if not defs:
		return operand
	return _Let(defs, operand)


class Dynamic(operate.Unary):
	'''Introduces a dynamic scope around a transformation, allowing them
	to be called outside the original scope, while preserving the original 
	context.
	
	@param operand: a transformation.
	@param ctx: the context to be passed to the operand.
	'''
	
	def __init__(self, operand, ctx):
		operate.Unary.__init__(self, operand)
		self.ctx = ctx
		
	def apply(self, term, ctx):
		return self.operand.apply(term, self.ctx)

