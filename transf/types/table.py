'''Hash table variable.'''


import aterm.factory

from transf import exception
from transf import context
from transf import transformation
from transf import operate
from transf import variable
#from transf.lib import base
#from transf.lib import combine
#from transf.lib import build
#from transf.lib import build
from transf.util import TransformationMethod


_factory = aterm.factory.factory


class Table(variable.Variable):
	'''A table is mapping of terms to terms.'''

	def _table(self, ctx):
		tbl = ctx.get(self.name)
		if tbl is None:
			tbl = {}
			ctx.set(self.name, tbl)
		return tbl

	@TransformationMethod
	def set(self, trm, ctx):
		'''Setting a [key, value] list will add the pair to the table. Setting
		a [key] list will remove the key and its value from the table.'''
		# TODO: better exception handling
		tbl = self._table(ctx)
		if trm:
			key = trm.head
			tail = trm.tail
			if tail:
				val = trm.head
				tbl[key] = val
			else:
				try:
					return tbl.pop(key)
				except KeyError:
					raise exception.Failure("term not in table", key)
		else:
			self.clear()
		return trm

	@TransformationMethod
	def clear(self, trm, ctx):
		'''Clears all elements of the table.'''
		ctx.set(self.name, {})
		return trm

	@TransformationMethod
	def match(self, trm, ctx):
		'''Lookups the key matching the term in the table.'''
		tbl = self._table(ctx)
		try:
			tbl[trm]
		except KeyError:
			raise exception.Failure("term not in table", trm)
		else:
			return trm

	@TransformationMethod
	def build(self, trm, ctx):
		'''Builds a list all keys in the table.'''
		tbl = self._table(ctx)
		return _factory.makeList(tbl.keys())

	@TransformationMethod
	def congruent(self, trm, ctx):
		'''Lookups the key matching to the term in the table and return its
		associated value.
		'''
		tbl = self._table(ctx)
		try:
			return tbl[trm]
		except KeyError:
			raise exception.Failure("term not in table", trm)

	def Add(self, other):
		return Add(self, other)

#	def sub(self, other):
#		for key in self.terms.iterkeys():
#			if key not in other.terms:
#				del self.terms[key]
#
#	def equals(self, other):
#		if len(self.terms) != len(other.terms):
#			return False
#		for key, value in self.terms.iteritems():
#			try:
#				if value != other.terms[key]:
#					return False
#			except KeyError:
#				return False
#		return True


class Add(transformation.Transformation):

	def __init__(self, var1, var2):
		transformation.Transformation.__init__(self)
		self.var1 = var1
		self.var2 = var2

	def apply(self, trm, ctx):
		tbl1 = self.var1._table(ctx)
		tbl2 = self.var2._table(cx)
		tbl1.update(tbl2)
		return trm


class Join(operate.Binary):
	'''Transformation composition which joins (unites/intersects) tables in
	the process.
	'''

	def __init__(self, loperand, roperand, unames, inames):
		operate.Binary.__init__(self, loperand, roperand)
		self.unames = unames
		self.inames = inames

	def apply(self, term, ctx):
		# duplicate tables
		lvars = []
		rvars = []
		utbls = []
		itbls = []
		for name in self.unames:
			tbl = ctx.get(name)
			ltbl = tbl.copy()
			lvars.append((name, ltbl))
			rtbl = tbl.copy()
			rvars.append((name, rtbl))
			utbls.append((tbl, ltbl, rtbl))
		for name in self.inames:
			tbl = ctx.get(name)
			ltbl = tbl.copy()
			lvars.append((name, ltbl))
			rtbl = tbl.copy()
			rvars.append((name, rtbl))
			itbls.append((tbl, ltbl, rtbl))
		lctx = context.Context(lvars, ctx)
		rctx = context.Context(rvars, ctx)

		# apply transformations
		term = self.loperand.apply(term, lctx)
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


class Iterate(operate.Unary):
	'''Transformation composition which joins (unites/intersects) tables in
	the process.
	'''

	def __init__(self, operand, unames, inames):
		operate.Unary.__init__(self, operand)
		self.unames = unames
		self.inames = inames

	def apply(self, term, ctx):
		assert 0
		# duplicate tables
		lvars = []
		rvars = []
		utbls = []
		itbls = []
		for name in self.unames:
			tbl = name._table(ctx)
			ltbl = tbl.copy()
			lvars.append((name, ltbl))
			rtbl = tbl.copy()
			rvars.append((name, rtbl))
			utbls.append((tbl, ltbl, rtbl))
		for name in self.inames:
			tbl = name._table(ctx)
			ltbl = tbl.copy()
			lvars.append((name, ltbl))
			rtbl = tbl.copy()
			rvars.append((name, rtbl))
			itbls.append((tbl, ltbl, rtbl))
		rctx = context.Context(rvars, ctx)

		# iterate
		while True:
			# apply transformation
			res = self.operand.apply(term, rctx)

			# join the tables
			equals = True
			for tbl, ltbl, rtbl in utbls:
				# unite
				equals = equals and ltbl.equals(rtbl)
				ltbl.add(rtbl)
			for tbl, ltbl, rtbl in itbls:
				# intersect
				equals = equals and ltbl.equals(rtbl)
				ltbl.sub(rtbl)
			if equals:
				break

		# copy final result
		for tbl, ltbl, rtbl in utbls:
			tbl.unset()
			tbl.add(ltbl)
		for tbl, ltbl, rtbl in itbls:
			tbl.unset()
			tbl.add(ltbl)

		return res
