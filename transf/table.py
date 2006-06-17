'''Hash table transformations.'''


import aterm.factory

from transf import exception
from transf import context
from transf import variable
from transf import base
from transf import operate


_factory = aterm.factory.Factory()


class Table(variable.Variable):
	'''A table is mapping of terms to terms.'''
	
	def __init__(self, terms = ()):
		variable.Variable.__init__(self)
		self.terms = dict(terms)
	
	def copy(self):
		return Table(self.terms)
	
	def set(self, key, term):
		self.terms[key] = term
		return term
	
	def get(self, key):
		try:
			return self.terms[key]
		except KeyError:
			raise exception.Failure("term not in table", key)
	
	def pop(self, key):
		try:
			return self.terms.pop(key)
		except KeyError:
			raise exception.Failure("term not in table", key)
	
	def clear(self):
		self.terms.clear()
		
	def match(self, term):
		self.get(term)
		return term
	
	def build(self):
		return _factory.makeList(self.terms.iterkeys())
		
	def traverse(self, term):
		return self.get(term)
	
	def add(self, other):
		self.terms.update(other.terms)

	def sub(self, other):
		for key in self.terms.iteritems():
			if key not in other.terms:
				del self.terms[key]


class Get(variable.Transformation):
	'''Get an element of the table.'''

	def apply(self, term, ctx):
		tbl = ctx.get(self.name)
		return tbl.get(term)


class Set(variable.Transformation):
	'''Set an element of the table.'''

	def __init__(self, name, key):
		variable.Transformation.__init__(self, name)
		self.key = key

	def apply(self, term, ctx):
		tbl = ctx.get(self.name)
		key = self.key.apply(term, ctx)
		return tbl.set(key, term)


class Del(variable.Transformation):
	'''Pop an element of the table.'''

	def apply(self, term, ctx):
		tbl = ctx.get(self.name)
		return tbl.pop(term)


class Clear(variable.Transformation):
	'''Clear the table.'''
	
	def apply(self, term, ctx):
		tbl = ctx.get(self.name)
		tbl.clear()
		return term


class Join(operate.Binary):
	'''Transformation composition which joins (unites/intersects) tables in 
	the process.
	'''
	
	def __init__(self, loperand, roperand, unames, inames):
		operate.Binary.__init__(self, loperand, roperand)
		self.unames = unames
		self.inames = inames
	
	def apply(self, term, ctx):
		# copy tables
		names = self.unames + self.inames
		
		# duplicate tables
		lvars = []
		rvars = []
		utbls = []
		itbls = []
		for name in self.unames:
			tbl = ctx.get(name)
			ltbl = tbl.copy()
			rtbl = tbl.copy()
			utbls.append((tbl, ltbl, rtbl))
		for name in self.inames:
			tbl = ctx.get(name)
			ltbl = tbl.copy()
			rtbl = tbl.copy()
			itbls.append((tbl, ltbl, rtbl))

		# apply transformations
		lctx = context.Context(lvars, ctx)
		term = self.loperand.apply(term, lctx)
		rctx = context.Context(rvars, ctx)
		term = self.roperand.apply(term, rctx)

		# join the tables
		for tbl, ltbl, rtbl in utbls:
			# unite
			tbl.clear()
			tbl.add(ltbl)
			tbl.add(rtbl)
		for tbl, ltbl, rtbl in itbls:
			# intersect
			tbl.clear()
			tbl.add(ltbl)
			tbl.sub(rtbl)
		
		return term
