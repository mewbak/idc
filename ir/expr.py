'''Utility class for simplify coding of expressions using the builtin operators.
'''


import aterm.terms
import walker


class Expr:
	'''Utility class for simplify coding of expressions using the builtin operators.'''
	
	def __init__(self, term):
		self.term = term
		self.factory = term.factory
		
		self.sign = self.factory.make("Unknown")
		self.size = self.factory.makeInt(32)
		self.type = self.factory.make("Int(size,sign)", size=self.size, sign=self.sign)
		
	def _make(self, pattern, *args, **kargs):
		return Expr(self.term.factory.make(pattern, *args, **kargs))
	
	def _cast(self, other):
		if isinstance(other, Expr):
			return other
		if isinstance(other, aterm.terms.Term):
			return Expr(other)
		if isinstance(other, int):
			return self._make("Lit(Int(size,sign),value)",
				size = self.size,
				sign = self.sign,
				value = other
			)		
		if isinstance(other, float):
			# FIXME: size
			return self._make("Lit(Float(size),value)",
				size = self.size,
				sign = self.sign,
				value = other
			)
		else:
			raise TypeError, "don't know how to handle '%r'" % other

	_un_op_table = {
		'neg': 'Neg(size)',
		'invert': 'BitNot(size)',
	}
		
	_bin_op_table = {
		'add': 'Plus(type)',
		'sub': 'Minus(type)',
		'mul': 'Mult(type)',
		'div': 'Div(type)',
		'mod': 'Mod(type)',

		'and': 'BitAnd(size)',
		'xor': 'BitXor(size)',
		'or': 'BitOr(size)',
		'lshift': 'LShift(size)',
		'rshift': 'RShift(size)',
	}
	
	def __getattr__(self, name):
		if name.startswith('__') and name.endswith('__'):
			op = name[2:-2]
			if op in self._un_op_table:
				op = self.factory.make(self._un_op_table[op], type = self.type, size = self.size, sign = self.sign)
				return lambda: self._make("Unary(op,expr)", op = op, expr=self.term)
			if op in self._bin_op_table:
				op = self.factory.make(self._bin_op_table[op], type = self.type, size = self.size, sign = self.sign)
				return lambda other: self._make("Binary(op,lexpr,rexpr)", op = op, lexpr=self.term, rexpr=self._cast(other).term)
			if op.startswith('r'):
				op = op[1:]
				if op in self._bin_op_table:
					op = self.factory.make(self._bin_op_table[op], type = self.type, size = self.size, sign = self.sign)
					return lambda other: self._make("Binary(op,lexpr,rexpr)", op = op, rexpr=self.term, lexpr=self._cast(other).term)
		
		raise AttributeError, "attribute not found '%r'" % name

