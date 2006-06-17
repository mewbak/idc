'''Term building transformations.'''


import aterm.factory
import aterm.types
import aterm.terms

from transf import base
from transf import exception
from transf import operate
from transf import _helper


_factory = aterm.factory.Factory()


class _Term(base.Transformation):

	# NOTE: this class should not be derived to avoid 
	# breaking optimizations
	
	def __init__(self, term):
		base.Transformation.__init__(self)
		self.term = term
	
	def apply(self, term, ctx):
		return self.term

def Term(term):
	if isinstance(term, basestring):
		term = _factory.parse(term)
	return _Term(term)


def Int(value):
	term = _factory.makeInt(value)
	return _Term(term)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)


def Real(value):
	return _Term(_factory.makeReal(value))


def Str(value):
	return _Term(_factory.makeStr(value))

empty = Str("")


_nil = _factory.makeNil()

def Nil():
	return _Term(_nil)

nil = Nil()


class _Cons(base.Transformation):
	
	def __init__(self, head, tail):
		base.Transformation.__init__(self)
		self.head = head
		self.tail = tail
		
	def apply(self, term, ctx):
		head = self.head.apply(term, ctx)
		tail = self.tail.apply(term, ctx)
		return term.factory.makeCons(head, tail)

def Cons(head, tail):
	if isinstance(tail, (tuple, list)):
		tail = List(tail)
	if isinstance(head, _Term) and isinstance(tail, _Term):
		return _Term(_factory.makeCons(head.term, tail.term))
	return _Cons(head, tail)


def List(elms, tail = None):
	if tail is None:
		tail = nil
	return operate.Nary(iter(elms), Cons, tail)


class _Appl(base.Transformation):
	
	def __init__(self, name, args):
		base.Transformation.__init__(self)
		self.name = name
		self.args = args
		
	def apply(self, term, ctx):
		name = self.name.apply(term, ctx)
		args = self.args.apply(term, ctx)
		return term.factory.makeAppl(name, args)

def Appl(name, args):
	if isinstance(name, basestring):
		name = Str(name)
	if isinstance(args, (tuple, list)):
		args = List(args)
	if isinstance(name, _Term) and isinstance(args, _Term):
		return _Term(_factory.makeAppl(name.term, args.term))
	return _Appl(name, args)


class Var(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, ctx):
		var = ctx.get(self.name)
		return var.build()


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos

	def apply(self, term, ctx):
		return term.setAnnotations(self.annos.apply(term, ctx))

	
class Pattern(base.Transformation):

	# TODO: Parse patterns into the above classes

	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, ctx):
		# FIXME: avoid the dict copy
		kargs = {}
		for name, var in ctx:
			kargs[name] = var.build()
		return self.pattern.make(term, **kargs)


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)
