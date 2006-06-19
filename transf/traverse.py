'''Term traversal transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import util
from transf import variable
from transf import operate
from transf import combine
from transf import match
from transf import congruent


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
	map.subject = match.nil | Cons(operand, map)
	return map


def MapR(operand):
	return Map(operand, congruent.ConsR)


def Filter(operand):
	return Map(operand, ConsFilter)


def FilterR(operand):
	return Map(operand, ConsFilterR)


def Fetch(operand):
	fetch = util.Proxy()
	fetch.subject = Cons(operand, base.ident) | Cons(base.ident, fetch)
	return fetch


class _Subterms(base.Transformation):
	
	def __init__(self, list, lit):
		base.Transformation.__init__(self)
		self.lit = lit
		self.list = list
		self.appl = congruent.Appl(base.ident, list)
		
	def apply(self, term, ctx):
		if term.type == aterm.types.APPL:
			return self.appl.apply(term, ctx)
		elif term.type & aterm.types.LIST:
			return self.list.apply(term, ctx)
		else:
			return self.lit.apply(term, ctx)


def All(operand):
	'''Applies a transformation to all direct subterms of a term.'''
	return _Subterms(Map(operand), base.ident)


def One(operand):
	'''Applies a transformation to exactly one direct subterm of a term.'''
	one = util.Proxy()
	one.subject = _Subterms(
		congruent.Cons(operand, base.ident) | congruent.Cons(base.ident, one), 
		base.fail
	)
	return one


def Some(operand):
	'''Applies a transformation to as many direct subterms of a term, but at list one.'''
	some = util.Proxy()
	some.subject = _Subterms(
		congruent.Cons(operand, Map(combine.Try(operand))) | congruent.Cons(base.ident, some),
		base.fail
	)
	return some


def DownUp(down = None, up = None, stop = None):
	downup = util.Proxy()
	downup.subject = All(downup)
	if stop is not None:
		downup.subject = stop | downup.subject
	if up is not None:
		downup.subject = downup.subject & up
	if down is not None:
		downup.subject = down & downup.subject
	return downup


def TopDown(operand, stop = None):
	return DownUp(down = operand, stop = stop)


def BottomUp(operand, stop = None):
	return DownUp(up = operand, stop = stop)


def InnerMost(operand):
	innermost = util.Proxy()
	innermost.subject = BottomUp(combine.Try(operand & innermost))
	return innermost


def AllTD(operand):
	'''Apply a transformation to all subterms, but stops recursing 
	as soon as it finds a subterm to which the transformation succeeds.
	'''
	alltd = util.Proxy()
	alltd.subject = operand | All(alltd)
	return alltd
'''Term traversal transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import util
from transf import variable
from transf import operate
from transf import combine
from transf import match
from transf import congruent


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
	map.subject = match.nil | Cons(operand, map)
	return map


def MapR(operand):
	return Map(operand, congruent.ConsR)


def Filter(operand):
	return Map(operand, ConsFilter)


def FilterR(operand):
	return Map(operand, ConsFilterR)


def Fetch(operand):
	fetch = util.Proxy()
	fetch.subject = Cons(operand, base.ident) | Cons(base.ident, fetch)
	return fetch


class _Subterms(base.Transformation):
	
	def __init__(self, list, lit):
		base.Transformation.__init__(self)
		self.lit = lit
		self.list = list
		self.appl = congruent.Appl(base.ident, list)
		
	def apply(self, term, ctx):
		if term.type == aterm.types.APPL:
			return self.appl.apply(term, ctx)
		elif term.type & aterm.types.LIST:
			return self.list.apply(term, ctx)
		else:
			return self.lit.apply(term, ctx)


def All(operand):
	'''Applies a transformation to all direct subterms of a term.'''
	return _Subterms(Map(operand), base.ident)


def One(operand):
	'''Applies a transformation to exactly one direct subterm of a term.'''
	one = util.Proxy()
	one.subject = _Subterms(
		congruent.Cons(operand, base.ident) | congruent.Cons(base.ident, one), 
		base.fail
	)
	return one


def Some(operand):
	'''Applies a transformation to as many direct subterms of a term, but at list one.'''
	some = util.Proxy()
	some.subject = _Subterms(
		congruent.Cons(operand, Map(combine.Try(operand))) | congruent.Cons(base.ident, some),
		base.fail
	)
	return some


def DownUp(down = None, up = None, stop = None):
	downup = util.Proxy()
	downup.subject = All(downup)
	if stop is not None:
		downup.subject = stop | downup.subject
	if up is not None:
		downup.subject = downup.subject & up
	if down is not None:
		downup.subject = down & downup.subject
	return downup


def TopDown(operand, stop = None):
	return DownUp(down = operand, stop = stop)


def BottomUp(operand, stop = None):
	return DownUp(up = operand, stop = stop)


def InnerMost(operand):
	innermost = util.Proxy()
	innermost.subject = BottomUp(combine.Try(operand & innermost))
	return innermost


def AllTD(operand):
	'''Apply a transformation to all subterms, but stops recursing 
	as soon as it finds a subterm to which the transformation succeeds.
	'''
	alltd = util.Proxy()
	alltd.subject = operand | All(alltd)
	return alltd
