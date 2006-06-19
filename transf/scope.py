'''Transformations which introduce new scopes.'''


from transf import context
from transf import term
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
	vars = [(name, term.Term) for name in names]
	return _Local(vars, operand)


def Local2(vars, operand):
	if not vars:
		return operand
	return _Local(vars, operand)


def Local3(names, operand):
	if not names:
		return operand
	vars = [(name, term.Term) for name in names]
	return _Local(vars, operand)


class _Let(operate.Unary):
	
	def __init__(self, defs, operand):
		operate.Unary.__init__(self, operand)
		self.defs = defs
		
	def apply(self, trm, ctx):
		vars = [(name, term.Term(transf.apply(trm, ctx))) for name, transf in self.defs]
		ctx = context.Context(vars, ctx)
		return self.operand.apply(trm, ctx)

def Let(operand, **defs):
	if not defs:
		return operand
	return _Let(defs.items(), operand)

def Let2(defs, operand):
	if not defs:
		return operand
	return _Let(defs, operand)


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

