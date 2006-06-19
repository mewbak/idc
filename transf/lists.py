'''List manipulation transformations.

See also U{http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-unstable-latest/manual/chunk-chapter/library-lists.html}.
'''


from transf import exception
from transf import base
from transf import util
from transf import operate
from transf import project
from transf import match
from transf import build
from transf import congruent
from transf import scope
from transf import unify


length = unify.Count(base.ident)


class ConsFilter(congruent.Cons):
	
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure
		
		try:
			new_head = self.head.apply(old_head, ctx)
		except exception.Failure:
			return self.tail.apply(old_tail, ctx)
		new_tail = self.tail.apply(old_tail, ctx)
		
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


class ConsFilterR(congruent.Cons):
	
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure
		
		new_tail = self.tail.apply(old_tail, ctx)
		try:
			new_head = self.head.apply(old_head, ctx)
		except exception.Failure:
			return new_tail

		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


def Map(operand, Cons = congruent.Cons):
	map = util.Proxy()
	map.subject = match.nil + Cons(operand, map)
	return map


def MapR(operand):
	return Map(operand, congruent.ConsR)


def Filter(operand):
	return Map(operand, ConsFilter)


def FilterR(operand):
	return Map(operand, ConsFilterR)


def Fetch(operand):
	fetch = util.Proxy()
	fetch.subject = \
		congruent.Cons(operand, base.ident) + \
		congruent.Cons(base.ident, fetch)
	return fetch


def FetchElem(operand):
	fetch = util.Proxy()
	fetch.subject = \
		project.head * operand + \
		project.tail * fetch
	return fetch


class _Concat2(operate.Binary):
	
	def apply(self, term, ctx):
		head = self.loperand.apply(term, ctx)
		tail = self.roperand.apply(term, ctx)
		try:
			return head.extend(tail)
		except AttributeError:
			raise exception.Failure('not term lists', head, tail)

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


def MapCat(operand):
	return Map(operand, Cons = Concat2)


def AtSuffix(operand):
	atsuffix = util.Proxy()
	atsuffix.subject = operand + congruent.Cons(base.ident, atsuffix)
	return atsuffix


def Split(operand):
	tail = scope.Anonymous('split-tail')
	return scope.Local3(
		(tail,),
		build.List((
			AtSuffix(
				match.Cons(operand, match.Var(tail)) *
				build.nil
			),
			build.Var(tail)
		))
	)


def Split2(operand):
	tail = scope.Anonymous('split-tail')
	return scope.Local3(
		(tail,),
		build.List((
			AtSuffix(
				congruent.Cons(operand, base.ident) *
				match.Var(tail) *
				build.nil
			),
			build.Var(tail)
		))
	)

def Split3(operand):
	elem = scope.Anonymous('split3-elem')
	tail = scope.Anonymous('split3-tail')
	return scope.Local3(
		(elem, tail),
		build.List((
			AtSuffix(
				match.Cons(operand * match.Var(elem), match.Var(tail)) *
				build.nil
			),
			build.Var(elem),
			build.Var(tail)
		))
	)
	

class Lookup(base.Transformation):
	
	def __init__(self, key, table):
		base.Transformation.__init__(self)
		self.key = key
		self.table = table
	
	def apply(self, term, ctx):
		key = self.key.apply(term, ctx)
		table = self.table.apply(term, ctx)
		
		for name, value in table:
			if key.isEquivalent(name):
				return value
		raise exception.Failure('key not found in table', key, table)



