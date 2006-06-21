'''Common code for term matching, building, and congruent traversal 
transformations.
'''


import aterm.factory
import aterm.terms

from transf import base
from transf import operate


_factory = aterm.factory.factory


class _Term(base.Transformation):
	
	def __init__(self, term):
		base.Transformation.__init__(self)
		assert isinstance(term, aterm.terms.Term)
		self.term = term

def Term(term, _Term):
	if isinstance(term, basestring):
		term = _factory.parse(term)
	return _Term(term)


def Int(value, _Term):
	return _Term(_factory.makeInt(value))


def Real(value, _Term):
	return _Term(_factory.makeReal(value))


def Str(value, _Term):
	return _Term(_factory.makeStr(value))
	

def Nil(_Term):
	return _Term(_factory.makeNil())


class _Cons(base.Transformation):
	
	def __init__(self, head, tail):
		base.Transformation.__init__(self)
		self.head = head
		self.tail = tail

def Cons(head, tail, _Cons, _Term):
	if head is None:
		head = base.ident
	if tail is None:
		tail = base.ident
	if isinstance(head, _Term) and isinstance(tail, _Term):
		return _Term(_factory.makeCons(head.term, tail.term))
	return _Cons(head, tail)


def List(elms, tail, Cons, nil):
	if tail is None:
		tail = nil
	return operate.Nary(iter(elms), Cons, tail)


class _Appl(base.Transformation):

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		self.name = name
		self.args = args

def Appl(name, args, _Appl, _Term, List):
	if name is None:
		name = base.ident
	elif isinstance(name, basestring):
		name = _Term(_factory.makeStr(name))
	if args is None:
		args = base.ident
	elif isinstance(args, (tuple, list)):
		args = List(args)
	if isinstance(name, _Term) and isinstance(args, _Term):
		return _Term(_factory.makeAppl(name.term, args.term))
	return _Appl(name, args)


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos


class Pattern(base.Transformation):
	
	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
