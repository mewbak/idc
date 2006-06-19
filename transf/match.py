'''Term matching transformations.'''


import aterm.factory
import aterm.types
import aterm.terms

from transf import exception
from transf import base
from transf import variable
from transf import operate
from transf import _helper


_factory = aterm.factory.factory


class Type(base.Transformation):

	def __init__(self, type):
		base.Transformation.__init__(self)
		self.type = type

	def apply(self, term, ctx):
		if not term.type & self.type:
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


class Term(base.Transformation):
	
	def __init__(self, term):
		base.Transformation.__init__(self)
		if isinstance(term, basestring):
			self.term = _factory.parse(term)
		else:
			assert isinstance(term, aterm.terms.Term)
			self.term = term

	def apply(self, term, ctx):
		if self.term.isEquivalent(term):
			return term
		else:
			raise exception.Failure('term mismatch', self.term, term)


class TermSet(base.Transformation):
	
	def __init__(self, *terms):
		base.Transformation.__init__(self)
		self.terms = {}
		for term in terms:
			if isinstance(term, basestring):
				term = _factory.parse(term)
			else:
				assert isinstance(term, aterm.terms.Term)
			self.terms[term] = None
		
	def apply(self, term, ctx):
		if term in self.terms:
			return term
		else:
			raise exception.Failure('term not in set', term)


class Lit(base.Transformation):

	def __init__(self, type, value):
		base.Transformation.__init__(self)
		self.type = type
		self.value = value

	def apply(self, term, ctx):
		if term.type != self.type or term.value != self.value:
			raise exception.Failure
		return term


def Int(value):
	'''Transformation which matches an integer term with the given value.'''
	return Lit(aterm.types.INT, value)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)
	

def Real(value):
	'''Transformation which matches a real term with the given value.'''
	return Lit(aterm.types.REAL, value)


def Str(value):
	'''Transformation which matches a string term with the given value.'''
	return Lit(aterm.types.STR, value)
	

def StrSet(*values):
	return TermSet(*[_factory.makeStr(value) for value in values])
	

class Nil(base.Transformation):
	'''Transformation which matches an empty list term.'''

	def apply(self, term, ctx):
		if term.type != aterm.types.NIL:
			raise exception.Failure
		return term

nil = Nil()


class Cons(base.Transformation):
	'''Transformation which matches a list construction term.'''
	
	def __init__(self, head, tail):
		'''Takes as argument the transformations to be applied to the list 
		head and tail.'''
		self.head = head
		self.tail = tail
		
	def apply(self, term, ctx):
		try:
			self.head.apply(term.head, ctx)
			self.tail.apply(term.tail, ctx)
		except AttributeError:
			raise exception.Failure
		else:	
			return term

class ConsR(Cons):
	'''Transformation which matches a list construction term.'''
	
	def apply(self, term, ctx):
		try:
			self.head.apply(term.head, ctx)
			self.tail.apply(term.tail, ctx)
		except AttributeError:
			raise exception.Failure
		else:	
			return term


def List(elms, tail = None):
	if tail is None:
		tail = nil
	return operate.Nary(iter(elms), Cons, tail)
	

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
		try:
			name = term.name
			args = term.args
		except AttributeError:
			raise exception.Failure
		else:
			self.name.apply(name, ctx)
			self.args.apply(args, ctx)
			return term


Var = variable.Match


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos

	def apply(self, term, ctx):
		self.annos.apply(term.getAnnotations(), ctx)
		return term


def Anno(anno):
	from transf import traverse
	return Annos(traverse.One(Where(anno)))


class Pattern(base.Transformation):
	
	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, ctx):
		match = self.pattern.match(term)
		if not match:
			raise exception.Failure('pattern mismatch', self.pattern, term)
		for name, value in match.kargs.iteritems():
			var = ctx.get(name)
			var.match(value)
		return term


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)
