'''Hash table transformations.'''


from transf import exception
from transf import base
from transf import _operate


class Table(dict):
	'''A table is merely a dictionary of terms to terms.'''
	
	pass
	

class New(base.Transformation):
	'''Create a new table in the context.
	A variable must be declared in the context.
	'''

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, ctx):
		tbl = Table()
		try:
			res = ctx.setdefault(self.name, tbl)
		except KeyError:
			raise exception.Failure('undeclared table', self.name)
		if res is not tbl:
			raise exception.Failure('attempt to redefine table', self.name)
		return term


class _Base(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
		
	def _get_table(self, ctx):
		try:
			tbl = ctx[self.name]
		except KeyError:
			raise exception.Failure('undeclared table', self.name)
		if isinstance(tbl, Table):
			return tbl
		if tbl is None:
			raise exception.Failure('undefined table', self.name)
		raise exception.Failure('not a table', self.name)
			
	
class Get(_Base, _operate.UnaryMixin):
	'''Get an element of the table.'''

	# XXX: shouldn't this be a nullary op?
	
	def __init__(self, name, operand):
		_Base.__init__(self, name)
		_operate.UnaryMixin.__init__(self, operand)
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		key = self.operand.apply(term, ctx)
		try:
			return tbl[key]
		except KeyError:
			raise exception.Failure('key not found', self.name, key)


class Set(_Base, _operate.BinaryMixin):
	'''Set an element of the table.'''
	
	def __init__(self, name, loperand, roperand):
		_Base.__init__(self, name)
		_operate.BinaryMixin.__init__(self, loperand, roperand)
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		key = self.loperand.apply(term, ctx)
		val = self.roperand.apply(term, ctx)
		tbl[key] = val
		return term


class Clear(_Base):
	'''Clear the table.'''
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		tbl.clear()
		return term


# TODO: write union and intersection operators