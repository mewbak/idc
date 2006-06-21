'''Term matching transformations.'''


import aterm.factory
import aterm.types
import aterm.terms

from transf import exception
from transf import base
from transf import variable
from transf import combine
from transf import _common
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


class _Term(_common._Term):
	
	def apply(self, term, ctx):
		if self.term == term:
			return term
		else:
			raise exception.Failure('term mismatch', self.term, term)

def Term(term):
	return _common.Term(term, _Term)


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


def Int(value):
	'''Transformation which matches an integer term with the given value.'''
	return _common.Int(value, _Term)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)
	

def Real(value):
	'''Transformation which matches a real term with the given value.'''
	return _common.Real(value, _Term)


def Str(value):
	'''Transformation which matches a string term with the given value.'''
	return _common.Str(value, _Term)

empty = Str("")


def StrSet(*values):
	return TermSet(*[_factory.makeStr(value) for value in values])
	

class Nil(_Term):
	'''Transformation which matches an empty list term.'''

	# XXX: we subclass _Term in orde to save time in apply
	
	def __init__(self):
		_Term.__init__(self, _factory.makeNil())
		
	def apply(self, term, ctx):
		if term.type != aterm.types.NIL:
			raise exception.Failure
		return term

nil = Nil()


class _ConsL(_common._Cons):
	
	def apply(self, term, ctx):
		try:
			head = term.head
			tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list construction term', term)
		else:	
			self.head.apply(head, ctx)
			self.tail.apply(tail, ctx)
			return term

def ConsL(head, tail):
	return _common.Cons(head, tail, _ConsL, _Term)


class _ConsR(_common._Cons):
	
	def apply(self, term, ctx):
		try:
			head = term.head
			tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list construction term', term)
		else:	
			self.tail.apply(tail, ctx)
			self.head.apply(head, ctx)
			return term

def ConsR(head, tail):
	return _common.Cons(head, tail, _ConsR, _Term)


Cons = ConsL


def List(elms, tail = None):
	return _common.List(elms, tail, Cons, nil)
	

class _Appl(_common._Appl):

	def apply(self, term, ctx):
		try:
			name = term.name
			args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)
		else:
			self.name.apply(name, ctx)
			self.args.apply(args, ctx)
			return term


def Appl(name, args):
	return _common.Appl(name, args, _Appl, _Term, List)


Var = variable.Match


class Annos(_common.Annos):
	
	def apply(self, term, ctx):
		self.annos.apply(term.getAnnotations(), ctx)
		return term


def Anno(anno):
	from transf import traverse
	return Annos(traverse.One(combine.Where(anno)))


class Pattern(_common.Pattern):
	
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
