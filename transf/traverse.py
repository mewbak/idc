'''Term traversal transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import operate
from transf import combine
from transf import match
from transf import _helper


class Cons(base.Transformation):
	
	def __init__(self, head, tail):
		'''Takes as argument the transformations to be applied to the list 
		head and tail.'''
		self.head = head
		self.tail = tail
		
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)
		
		new_head = self.head.apply(old_head, ctx)
		new_tail = self.tail.apply(old_tail, ctx)
		
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


class ConsR(Cons):
	
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)
		
		new_tail = self.tail.apply(old_tail, ctx)
		new_head = self.head.apply(old_head, ctx)
		
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


class ConsFilter(Cons):
	
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


class ConsFilterR(Cons):
	
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


def List(elms, tail = None):
	'''Transformation which traverses a term list. 
	
	@param elms: sequence of transformations to be applied to the elements
	@param tail: option transformation to be applied to the list tail; defaults 
	to matching the empty list
	'''
	if tail is None:
		tail = match.nil
	return operate.Nary(iter(elms), Cons, tail)
	

class Appl(base.Transformation):
	'''Traverse a term application.'''

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = match.Str(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = List(args)
		else:
			self.args = args
				
	def apply(self, term, ctx):
		try:
			old_name = term.name
			old_args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)
		
		new_name = self.name.apply(old_name, ctx)
		new_args = self.args.apply(old_args, ctx)
		
		if new_name is not old_name or new_args is not old_args:
			return term.factory.makeAppl(
				new_name,
				new_args,
				term.annotations
			)
		else:
			return term


class Var(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		var = ctx.get(self.name)
		return var.traverse(term)


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos

	def apply(self, term, ctx):
		old_annos = term.getAnnotations()
		new_annos = self.annos.apply(old_annos, ctx)
		if new_annos is not old_annos:
			return term.setAnnotations(new_annos)
		else:
			return term


def Anno(anno):
	return Annos(One(anno))


_ = _helper.Factory(match.Int, match.Real, match.Str, List, Appl, Var, match.Pattern)


def Map(operand, Cons = Cons):
	map = base.Proxy()
	map.subject = match.nil | Cons(operand, map)
	return map


def MapR(operand):
	return Map(operand, ConsR)


def Filter(operand):
	return Map(operand, ConsFilter)


def FilterR(operand):
	return Map(operand, ConsFilterR)


def Fetch(operand):
	fetch = base.Proxy()
	fetch.subject = Cons(operand, base.ident) | Cons(base.ident, fetch)
	return fetch


class _Subterms(base.Transformation):
	
	def __init__(self, list, lit):
		base.Transformation.__init__(self)
		self.lit = lit
		self.list = list
		self.appl = Appl(base.ident, list)
		
	def apply(self, term, ctx):
		if term.type == aterm.types.APPL:
			return self.appl.apply(term, ctx)
		elif term.type == aterm.types.LIST:
			return self.list.apply(term, ctx)
		else:
			return self.lit.apply(term, ctx)


def All(operand):
	'''Applies a transformation to all direct subterms of a term.'''
	return _Subterms(Map(operand), base.ident)


def One(operand):
	'''Applies a transformation to exactly one direct subterm of a term.'''
	one = base.Proxy()
	one.subject = _Subterms(
		Cons(operand, base.ident) | Cons(base.ident, one), 
		base.fail
	)
	return one


def Some(operand):
	'''Applies a transformation to as many direct subterms of a term, but at list one.'''
	some = base.Proxy()
	some.subject = _Subterms(
		Cons(operand, Map(combine.Try(operand))) | Cons(base.ident, some),
		base.fail
	)
	return some


def DownUp(down = None, up = None, stop = None):
	downup = base.Proxy()
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
	innermost = base.Proxy()
	innermost.subject = BottomUp(combine.Try(operand & innermost))
	return innermost

def AllTD(operand):
	'''Apply a transformation to all subterms, but stops recursing 
	as soon as it finds a subterm to which the transformation succeeds.
	'''
	alltd = base.Proxy()
	alltd.subject = operand | All(alltd)
	return alltd