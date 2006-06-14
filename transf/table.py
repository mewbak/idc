'''Hash table transformations.'''


from transf import exception
from transf import context
from transf import base
from transf import _operate


class Table(dict):
	'''A table is mapping of terms to terms.'''
	
	def copy(self):
		return Table(self.iteritems())
	

class New(base.Transformation):
	'''Create a new table in the context.
	The name must be declared in the context.
	'''

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, ctx):
		tbl = Table()
		try:
			res = ctx.setdefault(self.name, tbl)
		except KeyError:
			raise exception.Fatal('undeclared table', self.name)
		if res is not tbl:
			raise exception.Fatal('attempt to redefine table', self.name)
		return term


def _get_table_from_context(name, ctx):
	# XXX: should we raise assertion errors here?
	try:
		tbl = ctx[name]
	except KeyError:
		raise exception.Fatal('undeclared table', name)
	if isinstance(tbl, Table):
		return tbl
	if tbl is None:
		raise exception.Fatal('undefined table', name)
	raise exception.Fatal('not a table', name)

	
class _Base(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
			
	
class Get(_Base, _operate.UnaryMixin):
	'''Get an element of the table.'''

	# XXX: shouldn't this be a nullary op?
	
	def __init__(self, name, operand):
		_Base.__init__(self, name)
		_operate.UnaryMixin.__init__(self, operand)
	
	def apply(self, term, ctx):
		tbl = _get_table_from_context(self.name, ctx)
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
		tbl = _get_table_from_context(self.name, ctx)
		key = self.loperand.apply(term, ctx)
		val = self.roperand.apply(term, ctx)
		tbl[key] = val
		return term


class Del(_Base, _operate.UnaryMixin):
	'''Delete an element of the table.'''

	# XXX: shouldn't this be a nullary op?
	
	def __init__(self, name, operand):
		_Base.__init__(self, name)
		_operate.UnaryMixin.__init__(self, operand)
	
	def apply(self, term, ctx):
		tbl = _get_table_from_context(self.name, ctx)
		key = self.operand.apply(term, ctx)
		try:
			del tbl[key]
		except KeyError:
			raise exception.Failure('key not found', self.name, key)
		return term


class Clear(_Base):
	'''Clear the table.'''
	
	def apply(self, term, ctx):
		tbl = _get_table_from_context(self.name, ctx)
		tbl.clear()
		return term


def _table_union(l, r):
	t = l.copy()
	t.update(r)
	return t


def _table_intersection(l, r):
	t = Table()
	for k, v in r.iteritems():
		if k in l:
			t[k] = v
	return t


class Merge(_operate.Binary):
	
	# TODO: support merging multiple tables
	
	def __init__(self, loperand, roperand, unames, inames):
		_operate.Binary.__init__(self, loperand, roperand)
		self.unames = unames
		self.inames = inames
	
	def apply(self, term, ctx):
		# copy tables
		names = self.unames + self.inames
		lctx = context.Context(names, ctx)
		rctx = context.Context(names, ctx)
		for name in names:
			tbl = _get_table_from_context(name, ctx)
			lctx[name] = tbl.copy()			
			rctx[name] = tbl.copy()

		# apply transformations
		term = self.loperand.apply(term, lctx)
		term = self.roperand.apply(term, rctx)

		# merge tables
		for name in self.unames:			
			ltbl = _get_table_from_context(name, lctx)
			rtbl = _get_table_from_context(name, rctx)
			ctx[name] = _table_union(ltbl, rtbl)
		for name in self.unames:			
			ltbl = _get_table_from_context(name, lctx)
			rtbl = _get_table_from_context(name, rctx)
			ctx[name] = _table_intersection(ltbl, rtbl)
		
		return term
