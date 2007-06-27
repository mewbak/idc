'''List manipulation transformations.

See also U{http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-unstable-latest/manual/chunk-chapter/library-lists.html}.
'''


import aterm.lists

from transf import exception
from transf import transformation
from transf import types
from transf import operate
from transf.lib import base
from transf.lib import util
from transf.lib import combine
from transf.lib import project
from transf.lib import match
from transf.lib import build
from transf.lib import congruent
from transf.lib import scope
from transf.lib import unify


# FIXME: write non-recursive versions

length = unify.Count(base.ident)


class Reverse(transformation.Transformation):

	def apply(self, term, ctx):
		return aterm.lists.reverse(term)

reverse = Reverse()


class Map(operate.Unary):

	def apply(self, trm, ctx):
		return aterm.lists.map(lambda trm: self.operand.apply(trm, ctx), trm)


def _Map(operand, Cons = congruent.Cons):
	map = util.Proxy()
	map.subject = match.nil + Cons(operand, map)
	return map


def MapR(operand):
	return _Map(operand, congruent.ConsR)


def ForEach(operand):
	return _Map(operand, match.Cons)


def Filter(operand):
	filter = util.Proxy()
	filter.subject = (
		match.nil +
		combine.GuardedChoice(
			congruent.Cons(operand, base.ident),
			congruent.Cons(base.ident, filter),
			project.tail * filter
		)
	)
	return filter

def FilterR(operand):
	filter = util.Proxy()
	filter.subject = (
		match.nil +
		congruent.Cons(base.ident, filter) *
		(congruent.Cons(operand, base.ident) + project.tail)
	)
	return filter


def Fetch(operand):
	fetch = util.Proxy()
	fetch.subject = (
		congruent.Cons(operand, base.ident) +
		congruent.Cons(base.ident, fetch)
	)
	return fetch


def FetchElem(operand):
	fetch = util.Proxy()
	fetch.subject = (
		project.head * operand +
		project.tail * fetch
	)
	return fetch


class _Concat2(operate.Binary):

	def apply(self, term, ctx):
		head = self.loperand.apply(term, ctx)
		tail = self.roperand.apply(term, ctx)
		return aterm.lists.extend(head, tail)


def Concat2(loperand, roperand):
	'''Concatenates two lists.'''
	if loperand is build.nil:
		return roperand
	if roperand is build.nil:
		return loperand
	return _Concat2(loperand, roperand)


def Concat(*operands):
	'''Concatenates several lists.'''
	return operate.Nary(operands, Concat2, build.nil)

concat = unify.Foldr(build.nil, Concat2)


def MapConcat(operand):
	return unify.Foldr(build.nil, Concat2, operand)


def AtSuffix(operand):
	atsuffix = util.Proxy()
	atsuffix.subject = operand + congruent.Cons(base.ident, atsuffix)
	return atsuffix


def AtSuffixR(operand):
	atsuffix = util.Proxy()
	atsuffix.subject = congruent.Cons(base.ident, atsuffix) + operand
	return atsuffix


# TODO: is there any way to avoid so much code duplication in the Split* transfs?

def Split(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				match.Cons(operand, match.Var(tail)) *
				build.nil
			),
			build.Var(tail)
		))
	)


def SplitBefore(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				congruent.Cons(operand, base.ident) *
				match.Var(tail) * build.nil
			),
			build.Var(tail)
		))
	)


def SplitAfter(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				congruent.Cons(operand, match.Var(tail) * build.nil)
			),
			build.Var(tail)
		))
	)


def SplitKeep(operand):
	elem = types.term.Term('elem')
	tail = types.term.Term('tail')
	return scope.Scope((elem, tail),
		build.List((
			AtSuffix(
				match.Cons(operand * match.Var(elem), match.Var(tail)) *
				build.nil
			),
			build.Var(elem),
			build.Var(tail)
		))
	)


def SplitAll(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			Split(operand),
			congruent.Cons(base.ident, project.head * splitall),
			build.List((base.ident,))
		)
	)
	return splitall


def SplitAllAfter(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			SplitAfter(operand),
			congruent.Cons(base.ident, project.head * splitall),
			build.List((base.ident,))
		)
	)
	return splitall


def SplitAllKeep(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			SplitKeep(operand),
			congruent.Cons(
				base.ident,
				congruent.Cons(
					base.ident,
					project.head * splitall
				)
			),
			build.List((base.ident,))
		)
	)
	return splitall


class Lookup(transformation.Transformation):

	def __init__(self, key, table):
		transformation.Transformation.__init__(self)
		self.key = key
		self.table = table

	def apply(self, term, ctx):
		key = self.key.apply(term, ctx)
		table = self.table.apply(term, ctx)

		for name, value in table:
			if key.isEquivalent(name):
				return value
		raise exception.Failure('key not found in table', key, table)



