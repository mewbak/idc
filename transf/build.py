'''Term building transformations.'''


import aterm.factory
import aterm.types

from transf import base
from transf import exception
from transf import _helper


_factory = aterm.factory.Factory()


class Term(base.Transformation):

	def __init__(self, term):
		base.Transformation.__init__(self)
		self.term = term
	
	def apply(self, term, context):
		return self.term


def Int(value):
	term = _factory.makeInt(value)
	return Term(term)

zero = Int(0)
one = Int(1)
two = Int(2)


def Real(value):
	term = _factory.makeReal(value)
	return Term(term)


def Str(value):
	term = _factory.makeStr(value)
	return Term(term)


def Nil():
	term = _factory.makeNil()
	return Term(term)

nil = Nil()


class Cons(base.Transformation):
	
	def __init__(self, head, tail):
		base.Transformation.__init__(self)
		self.head = head
		self.tail = tail
		
	def apply(self, term, context):
		head = self.head.apply(term, context)
		tail = self.tail.apply(term, context)
		return term.factory.makeCons(head, tail)


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
		name = self.name.apply(term, context)
		args = self.args.apply(term, context)
		return term.factory.makeAppl(name, args)


class Var(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, context):
		try:
			return context[self.name]
		except KeyError:
			raise exception.Failure('undefined variable', self.name)


class Pattern(base.Transformation):

	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, context):
		# FIXME: avoid the dict copy
		return self.pattern.make(term, **dict(context))


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)
