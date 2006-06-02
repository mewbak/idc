'''Term matching transformations.'''


import aterm.types

from transf import exception
from transf import base


class _Is(base.Transformation):

	def __init__(self, type):
		base.Transformation.__init__(self)
		self.type = type

	def apply(self, term, context):
		if term.type != self.type:
			raise exception.Failure
		return term


def IsInt():
	return _Is(aterm.types.INT)


def IsReal():
	return _Is(aterm.types.REAL)


def IsStr():
	return _Is(aterm.types.STR)


def IsList():
	return _Is(aterm.types.LIST)


def IsAppl():
	return _Is(aterm.types.APPL)


class _MatchLit(base.Transformation):

	def __init__(self, type, value):
		base.Transformation.__init__(self)
		self.type = type
		self.value = value

	def apply(self, term, context):
		if term.type != self.type or term.value != self.value:
			raise exception.Failure
		return term


def MatchInt(value):
	'''base.Transformation which matches an integer term with the given value.'''
	return _MatchLit(aterm.types.INT, value)
	

def MatchReal(value):
	'''base.Transformation which matches a real term with the given value.'''
	return _MatchLit(aterm.types.REAL, value)


def MatchStr(value):
	'''base.Transformation which matches a string term with the given value.'''
	return _MatchLit(aterm.types.STR, value)
	

class MatchNil(base.Transformation):
	'''base.Transformation which matches an empty list term.'''

	def apply(self, term, context):
		if term.type != aterm.types.LIST or not term.isEmpty():
			raise exception.Failure
		return term


class MatchCons(base.Transformation):
	'''base.Transformation which matches a list construction term.'''
	
	def __init__(self, head, tail):
		'''Takes as argument the transformations to be applied to the list 
		head and tail.'''
		self.head = head
		self.tail = tail
		
	def apply(self, term, context):
		try:
			self.head.apply(term.head)
			self.tail.apply(term.tail)
		except AttributeError:
			raise exception.Failure
		else:	
			return term


def _MatchList(elms_iter, tail):
	try:
		elm = elms_iter.next()
	except StopIteration:
		return tail
	else:
		return MatchCons(elm, _MatchList(elms_iter, tail))


def MatchList(elms):
	return _MatchList(iter(elms), MatchNil())
	

class MatchAppl(base.Transformation):

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = MatchStr(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = MatchList(args)
		else:
			self.args = args
		
	def apply(self, term, context):
		try:
			self.name.apply(term.name)
			self.args.apply(term.args)
		except AttributeError:
			raise exception.Failure
		else:	
			return term


class MatchVar(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, context):
		try:
			value = context[self.name]
		except KeyError:
			context[self.name] = term
		else:
			if not value.isEquivalent(term):
				raise exception.Failure
		return term
