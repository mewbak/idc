"""Dynamic rules support."""



from transf import exception
from transf import base
from transf import _operate


# XXX: lot of this code can be reused in tables


class Table(dict):
	'''A dynamic rule is a mapping from terms to transformations.'''
	pass
	

class New(base.Transformation):

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
			
	
class Apply(_Base, _operate.UnaryMixin):
	
	def __init__(self, name, operand):
		_Base.__init__(self, name)
		_operate.UnaryMixin.__init__(self, operand)
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		# TODO: is it possible to eliminate the linear search?
		for transf in self.transf.iteritems():
			try:
				return transf.apply(term, ctx)
			except exception.Failure:
				pass
		raise exception.Failure('failed to apply dynamic rule', self.name, term)


class Def(_Base, _operate.BinaryMixin):
	
	def __init__(self, name, loperand, roperand):
		_Base.__init__(self, name)
		_operate.BinaryMixin.__init__(self, loperand, roperand)
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		key = self.loperand.apply(term, ctx)
		val = scope.Dynamic(self.roperand, ctx)
		tbl[key] = val
		return term


class Undef(_Base, _operate.UnaryMixin):
	
	def __init__(self, name, operand):
		_Base.__init__(self, name)
		_operate.UnaryMixin.__init__(self, operand)
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		key = self.loperand.apply(term, ctx)
		del tbl[key]
		return term


class Clear(_Base):
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		tbl.clear()
		return term


class _Merge(_Base, _operate.BinaryMixin):
	
	def __init__(self, name, loperand, roperand, merge):
		_Base.__init__(self, name)
		_operate.BinaryMixin.__init__(self, loperand, roperand)
		self.merge = merge
	
	def apply(self, term, ctx):
		tbl = self._get_table(ctx)
		
		# apply first transformation
		ltbl = tbl.copy()
		lctx = context.Context((self.name,), ctx)
		lctx[self.name] = ltbl
		term = self.roperand.apply(term, lctx)

		# apply second with a copy of the original table
		rtbl = tbl.copy()
		rctx = context.Context((self.name,), ctx)
		rctx[self.name] = rtbl
		term = self.roperand.apply(term, rctx)
		
		# merge the tables
		tbl = self.merge(ltbl, rtbl)
		ctx[self.name] = tbl
		
		return term
		

def _union(l, r):
	t = l.copy()
	t.update(r)
	return t


def _intersect(l, r):
	t = {}
	for k, v in r:
		if k in l:
			t[k] = v
	return t


def Union(name, loperand, roperand):
	return _Merge(name, loperand, roperand, _union)
	
	
def Intersect(name, loperand, roperand):
	return _Merge(name, loperand, roperand, _intersect)

		