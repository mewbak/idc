'''Hash table variable.'''


import aterm.factory

from transf import exception
from transf import context
from transf import base
from transf import variable
from transf import operate
from transf import combine
from transf import build


_factory = aterm.factory.factory


class Table(variable.Variable):
	'''A table is mapping of terms to terms.'''
	
	def __init__(self, terms = ()):
		variable.Variable.__init__(self)
		self.terms = dict(terms)
	
	def copy(self):
		return Table(self.terms)
	
	def _set(self, key, val):
		self.terms[key] = val
	
	def _pop(self, key):
		try:
			return self.terms.pop(key)
		except KeyError:
			raise exception.Failure("term not in table", key)

	def set(self, term):
		'''Setting a [key, value] list will add the pair to the table. Setting
		a [key] list will remove the key and its value from the table.'''
		# TODO: better exception handling
		key = term.head
		tail = term.tail
		if tail:
			val = tail.head
			self._set(key, val)
		else:
			self._pop(key)
		
	def unset(self):
		'''Clears all elements of the table.'''
		self.terms.clear()
		
	def match(self, term):
		'''Lookups the key matching the term in the table.'''
		self.traverse(term)
	
	def build(self):
		'''Builds a list all keys in the table.'''
		return _factory.makeList(self.terms.iterkeys())
		
	def traverse(self, term):
		'''Lookups the key matching to the term in the table and return its 
		associated value.
		'''
		try:
			return self.terms[term]
		except KeyError:
			raise exception.Failure("term not in table", term)
	
	def add(self, other):
		self.terms.update(other.terms)

	def sub(self, other):
		for key in self.terms.iterkeys():
			if key not in other.terms:
				del self.terms[key]

	def __repr__(self):
		return '<%s.%s %r>' % (__name__, self.__class__.__name__, self.terms)


class New(variable.Constructor):
	'''Creates an empty table variable.'''
	def create(self, term, ctx):
		return Table()

new = New()


class Copy(variable.Constructor):
	'''Creates a table variable copied from other table variable.'''
	def __init__(self, name):
		variable.Constructor.__init__(self)
		self.name = name
	def create(self, term, ctx):
		var = ctx.get(self.name)
		return var.copy()


def Get(name):
	return variable.Traverse(name)


def Set(name, key):
	return combine.Where(build.List((key, base.ident)) & variable.Set(name))


def Del(name):
	return combine.Where(build.List((base.ident,)) & variable.Set(name))


def Clear(name):
	return variable.Unset(name)

	
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
			tbl.unset()
			tbl.add(ltbl)
			tbl.add(rtbl)
		for tbl, ltbl, rtbl in itbls:
			# intersect
			tbl.unset()
			tbl.add(ltbl)
			tbl.sub(rtbl)
		
		return term


