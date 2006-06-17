'''Term class hierarchy.'''


# pylint: disable-msg=W0142


from aterm import types
from aterm import exceptions
from aterm import _helpers


class Match(object):
	'''Match object.'''
	
	def __init__(self):
		self.args = []
		self.kargs = {}



class Term(object):
	'''Base class for all terms.
	
	Terms are non-modifiable. Changes are carried out by returning another term
	instance.
	'''

	# NOTE: most methods defer the execution to visitors
	
	__slots__ = ['factory', 'annotations']
	
	def __init__(self, factory, annotations = None):
		self.factory = factory
		if annotations:
			self.annotations = annotations
		else:			
			self.annotations = None
	
	# XXX: this has a large inpact in performance
	if __debug__ and False:
		def __setattr__(self, name, value):
			'''Prevent modification of term attributes.'''
			
			# TODO: implement this with a metaclass
			
			try:
				object.__getattribute__(self, name)
			except AttributeError:
				object.__setattr__(self, name, value)
			else:
				raise AttributeError("attempt to modify read-only term attribute '%s'" % name)		

	def __delattr__(self, name):
		'''Prevent deletion of term attributes.'''
		raise AttributeError("attempt to delete read-only term attribute '%s'" % name)		

	def getType(self):
		'''Gets the type of this term.'''
		return self.type
	
	def getHash(self):
		'''Generate a hash value for this term.'''
		return _helpers.Hash.hash(self)

	def getStructuralHash(self):
		'''Generate a hash value for this term. 
		Annotations are not taken into account.
		'''
		return _helpers.StructuralHash.hash(self)

	__hash__ = getStructuralHash
		
	def isConstant(self):
		'''Whether this term is constant, as opposed to have variables or wildcards.'''
		return _helpers.isConstant(self)

	def isEquivalent(self, other):
		'''Checks for structural equivalence of this term agains another term.'''
		return _helpers.isEquivalent(self, other)

	def isEqual(self, other):
		'''Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well.'''
		return _helpers.isEqual(self, other)
	
	def __eq__(self, other):
		if isinstance(other, Term):
			return _helpers.isEquivalent(self, other)
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def match(self, other):
		'''Matches this term pattern against a string or term.'''
		if isinstance(other, basestring):
			other = self.factory.parse(other)
		match = Match()
		comparator = _helpers.PatternComparator(match.args, match.kargs)
		if comparator.visit(self, other):
			return match
		else:
			return None
	
	def rmatch(self, other):
		'''Matches this term against a string or term pattern.'''
		if isinstance(other, basestring):
			other = self.factory.parse(other)
		return other.match(self)

	def getAnnotations(self):
		'''Returns the annotation list.'''
		if self.annotations is None:
			return self.factory.makeNil()
		else:
			return self.annotations

	def setAnnotations(self, annotations):
		'''Modify the annotation list.'''
		return _helpers.annotate(self, annotations)

	def getAnnotation(self, label):
		'''Gets an annotation associated'''
		if isinstance(label, basestring):
			label = self.factory.parse(label)
		annotations = self.annotations
		while annotations:
			if label.match(annotations.head):
				return annotations.head				
			annotations = annotations.tail
		raise ValueError("undefined annotation '%r'" % label)
	
	def setAnnotation(self, label, annotation):
		'''Returns a new version of this term with the 
		annotation associated with this label added or updated.'''
		if isinstance(label, basestring):
			label = self.factory.parse(label)
		remover = _helpers.Remover(label)
		if self.annotations:
			annotations = remover.visit(self.annotations)
		else:
			annotations = self.factory.makeNil()
		annotations = self.factory.makeCons(annotation, annotations)
		return self.setAnnotations(annotations)
				
	def removeAnnotation(self, label):
		'''Returns a new version of this term with the 
		annotation associated with this label removed.'''
		if isinstance(label, basestring):
			label = self.factory.parse(label)
		remover = _helpers.Remover(label)
		annotation = self.annotations
		if self.annotations:
			annotations = remover.visit(self.annotations)
			return self.setAnnotations(annotations)
		else:
			return self
		
	def make(self, *args, **kargs):
		'''Create a new term based on this term and a list of arguments.'''
		maker = _helpers.Maker(args, kargs)
		return maker.visit(self)

	def accept(self, visitor, *args, **kargs):
		'''Accept a visitor.'''
		raise NotImplementedError

	def writeToTextFile(self, fp):
		'''Write this term to a file object.'''
		writer = _helpers.TextWriter(fp)
		writer.visit(self)

	def __str__(self):
		'''Get the string representation of this term.'''
		try:
			from cStringIO import StringIO
		except ImportError:
			from StringIO import StringIO
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()
	
	def __repr__(self):
		return '<Term %s>' % (str(self),)


class Literal(Term):
	'''Base class for literal terms.'''

	__slots__ = ['value']
	
	def __init__(self, factory, value, annotations = None):
		Term.__init__(self, factory, annotations)
		self.value = value

	def getValue(self):
		return self.value

		
class Integer(Literal):
	'''Integer literal term.'''

	__slots__ = []
	
	type = types.INT

	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, (int, long)):
			raise TypeError('value is not an integer: %r' % value)
		Literal.__init__(self, factory, value, annotations)

	def __int__(self):
		return int(self.value)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitInt(self, *args, **kargs)


class Real(Literal):
	'''Real literal term.'''
	
	__slots__ = []
	
	type = types.REAL
	
	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, float):
			raise TypeError('value is not an integer: %r' % value)
		Literal.__init__(self, factory, value, annotations)

	def __float__(self):
		return float(self.value)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class String(Literal):
	'''String literal term.'''
	
	__slots__ = []
	
	type = types.STR
	
	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, str):
			raise TypeError('value is not an str: %r' % value)
		Literal.__init__(self, factory, value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class List(Term):
	'''Base class for list terms.'''

	__slots__ = []
	
	type = types.LIST
	
	def isEmpty(self):	
		raise NotImplementedError
	
	def __nonzero__(self):
		return not self.isEmpty()

	def getLength(self):
		raise NotImplementedError
	
	def __len__(self):
		return self.getLength()

	def getHead(self):
		raise NotImplementedError

	def getTail(self):
		raise NotImplementedError

	def __getitem__(self, index):
		raise NotImplementedError

	def __iter__(self):
		raise NotImplementedError

	def insert(self, index, element):
		raise NotImplementedError
	
	def append(self, element):
		return self.extend(self.factory.makeCons(element, self.factory.makeNil()))
		
	def extend(self, element):
		raise NotImplementedError
		
	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class Nil(List):
	'''Empty list term.'''
	
	__slots__ = []
	
	def __init__(self, factory, annotations = None):
		List.__init__(self, factory, annotations)

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		raise exceptions.EmptyListException
	
	def getTail(self):
		raise exceptions.EmptyListException

	def __getitem__(self, index):
		raise IndexError

	def __iter__(self):
		raise StopIteration
		yield None
		
	def insert(self, index, element):
		if not index:
			return self.factory.makeCons(element, self)
		else:
			raise IndexError
		
	def extend(self, tail):
		return tail
		
	def accept(self, visitor, *args, **kargs):
		return visitor.visitNil(self, *args, **kargs)


class Cons(List):
	'''Concatenated list term.'''
	
	__slots__ = ['head', 'tail']
	
	def __init__(self, factory, head, tail = None, annotations = None):
		List.__init__(self, factory, annotations)

		if not isinstance(head, Term):
			raise TypeError("head is not a term: %r" % head)
		self.head = head
		if tail is None:
			self.tail = self.factory.makeNil()
		else:
			if not isinstance(tail, (List, Variable, Wildcard)):
				raise TypeError("tail is not a list, variable, or wildcard term: %r" % tail)
			self.tail = tail
	
	def isEmpty(self):
		return False
	
	def getLength(self):
		return 1 + self.tail.getLength()
	
	def getHead(self):
		return self.head
	
	def getTail(self):
		return self.tail

	def __getitem__(self, index):
		if index == 0:
			return self.head
		else:
			return self.tail.__getitem__(index - 1)

	def __iter__(self):
		term = self
		while term:
			yield term.head
			term = term.tail
		raise StopIteration
		
	def insert(self, index, element):
		if not index:
			return self.factory.makeCons(element, self)
		else:
			return self.factory.makeCons(
				self.head,
				self.tail.insert(index - 1, element),
				self.annotations
			)
		
	def extend(self, tail):
		return self.factory.makeCons(
			self.head, 
			self.tail.extend(tail),
			self.annotations
		)
		
	def accept(self, visitor, *args, **kargs):
		return visitor.visitCons(self, *args, **kargs)


class Application(Term):
	'''Application term.'''

	__slots__ = ['name', 'args']
	
	type = types.APPL
	
	def __init__(self, factory, name, args = None, annotations = None):
		Term.__init__(self, factory, annotations)

		if not isinstance(name, (String, Variable, Wildcard)):
			raise TypeError("name is not a string, variable, or wildcard term: %r" % name)
		self.name = name
		if args is None:
			self.args = self.factory.makeNil()
		else:
			if not isinstance(args, (List, Variable, Wildcard)):
				raise TypeError("args is not a list term: %r" % args)
			self.args = args
	
	def getName(self):
		return self.name
	
	def getArity(self):
		return self.args.getLength()

	def getArgs(self):
		return self.args
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitAppl(self, *args, **kargs)


class Placeholder(Term):
	'''Base class for placeholder terms.'''

	__slots__ = []
	
	
class Wildcard(Placeholder):
	'''Wildcard term.'''

	__slots__ = []
	
	type = types.WILDCARD
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitWildcard(self, *args, **kargs)


class Variable(Placeholder):
	'''Variable term.'''
	
	__slots__ = ['name', 'pattern']

	type = types.VAR
	
	def __init__(self, factory, name, pattern, annotations = None):
		Placeholder.__init__(self, factory, annotations)
		self.name = name
		self.pattern = pattern
	
	def getName(self):
		return self.name

	def getPattern(self):
		return self.pattern

	def accept(self, visitor, *args, **kargs):
		return visitor.visitVar(self, *args, **kargs)

