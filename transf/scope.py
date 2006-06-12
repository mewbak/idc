'''Transformations which introduce new scopes.'''


from transf import context
from transf import _operate


class _Local(_operate.Unary):
	
	def __init__(self, operand, names):
		_operate.Unary.__init__(self, operand)
		self.names = names
		
	def apply(self, term, ctx):
		ctx = context.Context(self.names, ctx)
		return self.operand.apply(term, ctx)

def Local(operand, names = None):
	'''Introduces a new variable scope before the transformation.'''
	if not names:
		return operand
	return _Local(operand, names)
	

class _Let(_operate.Unary):
	
	def __init__(self, operand, defs):
		_operate.Unary.__init__(self, operand)
		self.defs = defs
		
	def apply(self, term, ctx):
		new_ctx = context.Context(self.defs.keys(), ctx)
		for name, transf in self.defs.iteritems():
			new_ctx[name] = transf.apply(term, ctx)
		return self.operand.apply(term, new_ctx)

def Let(operand, **defs):
	if not defs:
		return operand
	return _Let(operand, defs)

