'''Term matching transformations.'''


import aterm.factory
import aterm.types
import aterm.terms

from transf import exception
from transf import base
from transf import _operate
from transf import _helper


_factory = aterm.factory.Factory()


class Type(base.Transformation):

	def __init__(self, type):
		base.Transformation.__init__(self)
		self.type = type

	def apply(self, term, ctx):
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
	'''base.Transformation which matches an integer term with the given value.'''
	return Lit(aterm.types.INT, value)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)
	

def Real(value):
	'''base.Transformation which matches a real term with the given value.'''
	return Lit(aterm.types.REAL, value)


def Str(value):
	'''base.Transformation which matches a string term with the given value.'''
	return Lit(aterm.types.STR, value)
	

class Nil(base.Transformation):
	'''base.Transformation which matches an empty list term.'''

	def apply(self, term, ctx):
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
	return _operate.Nary(iter(elms), Cons, tail)
	

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


class Var(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		try:
			res = ctx.setdefault(self.name, term)
		except KeyError:
			raise exception.Failure('undeclared variable', self.name)
		if res is term or res.isEquivalent(term):
			return term
		else:
			raise exception.Failure('variable mismatch', self.name, res, term)


class VarUpdate(base.Transformation):
	
	# XXX: this class is somewhat displace here...
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		try:
			ctx[self.name] = term
		except KeyError:
			raise exception.Failure('undeclared variable', self.name)
		return term


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
			try:
				res = ctx.setdefault(name, value)
			except KeyError:
				raise exception.Failure('undeclared variable', name)
			if not (res is value or res.isEquivalent(value)):
				raise exception.Failure('variable mismatch', name, res, value)
		return term


_ = _helper.Factory(Int, Real, Str, List, Appl, Var, Pattern)
