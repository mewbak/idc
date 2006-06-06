'''Term matching transformations.'''


import aterm.factory
import aterm.types

from transf import exception
from transf import base
from transf import _helper


_factory = aterm.factory.Factory()


class Type(base.Transformation):

	def __init__(self, type):
		base.Transformation.__init__(self)
		self.type = type

	def apply(self, term, context):
		if term.type != self.type:
			raise exception.Failure
		return term


def AnInt():
	return Type(aterm.types.INT)

anInt = AnInt()


def AReal():
	return Type(aterm.types.REAL)

aReal = AReal()


def AStr():
	return Type(aterm.types.STR)

aStr = AStr()


def AList():
	return Type(aterm.types.LIST)

aList = AList()


def AnAppl():
	return Type(aterm.types.APPL)

anAppl = AnAppl()


class Lit(base.Transformation):

	def __init__(self, type, value):
		base.Transformation.__init__(self)
		self.type = type
		self.value = value

	def apply(self, term, context):
		if term.type != self.type or term.value != self.value:
			raise exception.Failure
		return term


def Int(value):
	'''base.Transformation which matches an integer term with the given value.'''
	return Lit(aterm.types.INT, value)
	

def Real(value):
	'''base.Transformation which matches a real term with the given value.'''
	return Lit(aterm.types.REAL, value)


def Str(value):
	'''base.Transformation which matches a string term with the given value.'''
	return Lit(aterm.types.STR, value)
	

class Nil(base.Transformation):
	'''base.Transformation which matches an empty list term.'''

	def apply(self, term, context):
		if term.type != aterm.types.LIST or not term.isEmpty():
			raise exception.Failure
		return term

nil = Nil()


class Cons(base.Transformation):
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


def _IterList(elms_iter, tail):
	try:
		elm = elms_iter.next()
	except StopIteration:
		return tail
	else:
		return Cons(elm, _IterList(elms_iter, tail))


def List(elms, tail = None):
	if tail is None:
		tail = Nil()
	return _IterList(iter(elms), tail)
	

class Appl(base.Transformation):

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = Str(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = List(args)
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


class Var(base.Transformation):
	
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


class Pattern(base.Transformation):
	
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


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)