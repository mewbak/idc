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
		if isinstance(term, basestring):
			self.term = _factory.parse(term)
		else:
			self.term = term
	
	def apply(self, term, ctx):
		return self.term


def Int(value):
	term = _factory.makeInt(value)
	return Term(term)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)


def Real(value):
	term = _factory.makeReal(value)
	return Term(term)


def Str(value):
	term = _factory.makeStr(value)
	return Term(term)


_nil = _factory.makeNil()

def Nil():
	return Term(_nil)

nil = Nil()


class Cons(base.Transformation):
	
	def __init__(self, head, tail):
		base.Transformation.__init__(self)
		self.head = head
		self.tail = tail
		
	def apply(self, term, ctx):
		head = self.head.apply(term, ctx)
		tail = self.tail.apply(term, ctx)
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
		
	def apply(self, term, ctx):
		name = self.name.apply(term, ctx)
		args = self.args.apply(term, ctx)
		return term.factory.makeAppl(name, args)


class Var(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, ctx):
		try:
			return ctx[self.name]
		except KeyError:
			raise exception.Failure('undefined variable', self.name)


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos

	def apply(self, term, ctx):
		return term.setAnnotations(self.annos.apply(term, ctx))

	
class Pattern(base.Transformation):

	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, ctx):
		# FIXME: avoid the dict copy
		return self.pattern.make(term, **dict(ctx))


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)
