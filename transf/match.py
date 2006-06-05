'''Term matching transformations.'''


import aterm.factory
import aterm.types

from transf import exception
from transf import base


_factory = aterm.factory.Factory()


class IsType(base.Transformation):

	def __init__(self, type):
		base.Transformation.__init__(self)
		self.type = type

	def apply(self, term, context):
		if term.type != self.type:
			raise exception.Failure
		return term


def IsInt():
	return IsType(aterm.types.INT)


def IsReal():
	return IsType(aterm.types.REAL)


def IsStr():
	return IsType(aterm.types.STR)


def IsList():
	return IsType(aterm.types.LIST)


def IsAppl():
	return IsType(aterm.types.APPL)


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
			self.head.apply(term.head, context)
			self.tail.apply(term.tail, context)
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


def MatchList(elms, tail = None):
	if tail is None:
		tail = MatchNil()
	return _MatchList(iter(elms), tail)
	

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
			self.name.apply(term.name, context)
			self.args.apply(term.args, context)
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


class MatchPattern(base.Transformation):
	
	
	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, context):
		match = self.pattern.match(term)
		if not match:
			raise exception.Failure('pattern mismatch', self.pattern, term)

		for name, value in match.kargs.iteritems():
			try:
				prev_value = context[name]
			except KeyError:
				context[name] = value
			else:
				if not value.isEquivalent(prev_value):
					raise exception.Failure

		return term

