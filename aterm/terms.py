'''Term class hierarchy.'''


__all__ = [
	'Term',
	'Literal',
	'Integer',
	'Real',
	'String',
	'Wildcard',
	'Variable',
	'List',
	'NilList',
	'ConsList',
	'Application',
]


try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

from aterm import types
from aterm import exceptions
from aterm import text


class Term:
	'''Base class for all terms.'''

	def __init__(self, factory, annotations = None):
		self.factory = factory
		self.__annotations = annotations
		
	def getFactory(self):
		'''Retrieves the factory responsible for creating this Term.'''
		return self.factory
		
	def getType(self):
		'''Gets the type of this term.'''
		raise NotImplementedError

	def getHash(self):
		'''Generate a hash value for this term.'''
		if self.__annotations is None:
			return self._getHash()
		else:
			return hash(self._getHash(), self.getAnnotations().getHash())

	def _getHash(self):
		raise NotImplementedError
	
	def __hash__(self):
		'''Shorthand for getHash().'''
		return self.getHash()
		
	def isConstant(self):
		'''Whether this term is types, as opposed to have variables or wildcards.'''
		raise NotImplementedError

	def isEquivalent(self, other):
		'''Checks for structural equivalence of this term agains another term.'''
		return self is other or self._isEquivalent(other)
		
	def _isEquivalent(self, other):
		raise NotImplementedError
	
	def match(self, other, args = None, kargs = None):
		'''Matches this term agains a string or term pattern.'''
		
		if isinstance(other, basestring):
			other = self.factory.parse(other)
		
		if args is None:
			args = []
		
		if kargs is None:
			kargs = {}
		
		try:
			self._match(other, args, kargs)
		except exceptions.PatternMismatchException:
			return False
		
		return True
	
	def _match(self, other, args, kargs):
		raise exceptions.PatternMismatchException

	def getAnnotation(self, label):
		'''Gets an annotation associated with label'''
		if not self.__annotations is None:
			annotations = self.__annotations
			while not annotations.isEmpty():
				if label.isEquivalent(annotations.getHead()):
					return annotations.getTail().getHead()				
				annotations = annotations.getTail().getTail()
		raise ValueError("undefined annotation '%r'" % label)
	
	def setAnnotation(self, label, annotation):
		'''Returns a new version of this term with the 
		annotation associated with this label added or updated.'''
		return self.setAnnotations(self._setAnnotation(label, annotation, self.getAnnotations()))

	def _setAnnotation(self, label, annotation, annotations):
		if annotations.isEmpty():
			return self.factory.makeConsList(label, self.factory.makeConsList(annotation, annotations))
			
		_label = annotations.getHead()
		annotations = annotations.getTail()
		_annotation = annotations.getHead()
		annotations = annotations.getTail()
		
		if label.isEquivalent(_label):
			return self.factory.makeConsList(label, self.factory.makeConsList(annotation, annotations))
		else:
			return self.factory.makeConsList(_label, self.factory.makeConsList(_annotation, self._setAnnotation(label, annotation, annotations)))
				
	def removeAnnotation(self, label):
		'''Returns a new version of this term with the 
		annotation associated with this label removed.'''
		return self.setAnnotations(self._removeAnnotation(label, self.getAnnotations()))
		
	def _removeAnnotation(self, label, annotations):
		if annotations.isEmpty():
			return annotations
			
		_label = annotations.getHead()
		annotations = annotations.getTail()
		_annotation = annotations.getHead()
		annotations = annotations.getTail()
		
		if label.isEquivalent(_label):
			return annotations
		else:
			return self.factory.makeConsList(_label, self.factory.makeConsList(_annotation, self._removeAnnotation(label, annotations)))

	def getAnnotations(self):
		'''Returns the annotation list.'''
		if self.__annotations is None:
			return self.factory.makeNilList()
		else:
			return self.__annotations

	def setAnnotations(self, annotations):
		raise NotImplementedError

	def __getattr__(self, name):
		'''Provide attributes 'type' and 'annotations', shorthand  for 
		getType() and getAnnotations() methods respectively.'''
		if name == 'type':
			return self.getType()
		elif name == 'annotations':
			return self.getAnnotations()
		else:
			raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
			
	def __setattr__(self, name, value):
		'''Prevent modification of term attributes'''
		
		if name in self.__dict__ or name in ('type', 'annotations'):
			raise TypeError("attempt to modify read-only term attribute '%s'" % name)
		else:
			self.__dict__[name] = value

	def isEqual(self, other):
		'''Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well.'''
		return self is other or self._isEqual(other) and self.annotations.isEquivalent(other.annotations)
		
	def _isEqual(self, other):
		raise NotImplementedError

	def __eq__(self, other):
		'''Shorthand for the isEqual method.'''
		return self.isEqual(other)

	def make(self, *args, **kargs):
		'''Create a new term based on this term and a list of arguments.'''
		return self._make(args, kargs)

	def _make(self, args, kargs):
		return self

	def accept(self, visitor, *args, **kargs):
		'''Accept a visitor.'''
		raise NotImplementedError

	def writeToTextFile(self, fp):
		'''Write this term to a file object.'''
		writer = text.TextWriter(fp)
		writer.visit(self)

	def __str__(self):
		'''Get the string representation of this term.'''
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()
	
	def __repr__(self):
		return str(self)


class Literal(Term):
	'''Base class for literal terms.'''

	def __init__(self, factory, value, annotations = None):
		Term.__init__(self, factory, annotations)
		self.value = value

	def _getHash(self):
		return hash(self.value)

	def getValue(self):
		return self.value

	def isConstant(self):
		return True
	
	def _isEquivalent(self, other):
		return self.getType() == other.getType() and self.value == other.value

	def _isEqual(self, other):
		return self._isEquivalent(other)

	def _match(self, other, args, kargs):
		if other.isEquivalent(self):
			return other
		else:
			return Term._match(self, other, args, kargs)

		
class Integer(Literal):
	'''Integer literal term.'''

	def getType(self):
		return types.INT

	def setAnnotations(self, annotations):
		return self.factory.makeInt(self.value, annotations)

	def accept(self, visitor):
		return visitor.visitInt(self)


class Real(Literal):
	'''Real literal term.'''
	
	def getType(self):
		return types.REAL

	def setAnnotations(self, annotations):
		return self.factory.makeReal(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class String(Literal):
	'''String literal term.'''
	
	def getType(self):
		return types.STR

	def getSymbol(self):
		return self.getValue()

	def setAnnotations(self, annotations):
		return self.factory.makeStr(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class List(Term):
	'''List term.'''

	def getType(self):
		return types.LIST

	def isEmpty(self):	
		return NotImplementedError
	
	def getLength(self):
		return NotImplementedError
	
	def __len__(self):
		return self.getLength()

	def getHead(self):
		return NotImplementedError

	def getTail(self):
		return NotImplementedError

	def __getitem__(self, index):
		if self.isEmpty():
			raise IndexError
		elif index == 0:
			return self.getHead()
		else:
			return self.getTail().__getitem__(index - 1)

	def insert(self, element):
		return self.factory.makeConsList(element, self)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class NilList(List):
	'''Empty list term.'''
	
	def __init__(self, factory, annotations = None):
		List.__init__(self, factory, annotations)

	def _getHash(self):
		return hash(())

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		raise exceptions.EmptyListException
	
	def getTail(self):
		raise exceptions.EmptyListException

	def isConstant(self):
		return True
	
	def _isEquivalent(self, other):
		return other.getType() == types.LIST and other.isEmpty()

	def _isEqual(self, other):
		return self._isEquivalent(other)

	def _match(self, other, args, kargs):
		if self is other:
			return other
		
		if other.getType() == types.LIST:
			if other.isEmpty():
				return other
				
		raise exceptions.PatternMismatchException

	def setAnnotations(self, annotations):
		return self.factory.makeNilList(annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitNilList(self, *args, **kargs)


class ConsList(List):
	'''Concatenated list term.'''
	
	def __init__(self, factory, head, tail = None, annotations = None):
		List.__init__(self, factory, annotations)

		if not isinstance(head, Term):
			raise TypeError("head is not a term: %r" % head)
		self.head = head
		if tail is None:
			self.tail = self.factory.makeNilList()
		else:
			if not isinstance(tail, (List, Variable, Wildcard)):
				raise TypeError("tail is not a list, variable, or wildcard term: %r" % tail)
			self.tail = tail
	
	def _getHash(self):
		return hash((self.head.getHash(), self.tail.getHash()))

	def isEmpty(self):
		return False
	
	def getLength(self):
		return 1 + self.tail.getLength()
	
	def getHead(self):
		return self.head
	
	def getTail(self):
		return self.tail

	def isConstant(self):
		return self.head.isConstant() and self.tail.isConstant()
	
	def _isEquivalent(self, other):
		return (
			other.getType() == types.LIST and not other.isEmpty() and 
			other.head.isEquivalent(self.head) and 
			other.tail.isEquivalent(self.tail)
		)
		
	def _isEqual(self, other):
		return (
			other.getType() == types.LIST and not other.isEmpty() and 
			other.head.isEqual(self.head) and 
			other.tail.isEqual(self.tail)
		)
	
	def _match(self, other, args, kargs):
		if self is other:
			return other
		
		if other.getType() == types.LIST:
			if not other.isEmpty():
				self.head._match(other.head, args, kargs)
				self.tail._match(other.tail, args, kargs)
				return other
		
		return List._match(self, other, args, kargs)

	def _make(self, args, kargs):
		return self.factory.makeConsList(self.head._make(args, kargs), self.tail._make(args, kargs), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeConsList(self.head, self.tail, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitConsList(self, *args, **kargs)


class Application(Term):
	'''Application term.'''

	def __init__(self, factory, name, args = None, annotations = None):
		Term.__init__(self, factory, annotations)

		if not isinstance(name, (String, Variable, Wildcard)):
			raise TypeError("name is not a string, variable, or wildcard term: %r" % name)
		self.name = name
		if args is None:
			self.args = self.factory.makeNilList()
		else:
			if not isinstance(args, (List, Variable, Wildcard)):
				raise TypeError("args is not a list term: %r" % args)
			self.args = args
	
	def getType(self):
		return types.APPL

	def _getHash(self):
		return hash((self.name.getHash(), self.args.getHash()))

	def getName(self):
		return self.name
	
	def getArity(self):
		return self.args.getLength()

	def getArgs(self):
		return self.args
	
	def isConstant(self):
		return self.name.isConstant() and self.args.isConstant()
	
	def _isEquivalent(self, other):
		return other.getType() == types.APPL and self.name.isEquivalent(other.name) and self.args.isEquivalent(other.args)

	def _isEqual(self, other):
		return other.getType() == types.APPL and self.name.isEqual(other.name) and self.args.isEqual(other.args)
		
	def _match(self, other, args, kargs):
		if other.getType() == types.APPL:
			self.name._match(other.name, args, kargs) 
			self.args._match(other.args, args, kargs)
			return other
		
		return Term._match(self, other, args, kargs)
	
	def _make(self, args, kargs):
		return self.factory.makeAppl(self.name._make(args, kargs), self.args._make(args, kargs), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeAppl(self.name, self.args, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitAppl(self, *args, **kargs)


class Wildcard(Term):
	'''Wildcard term.'''

	def getType(self):
		return types.WILDCARD
	
	def _getHash(self):
		return hash(None)
		
	def getSymbol(self):
		return '_'
	
	def isConstant(self):
		return False
	
	def _isEquivalent(self, other):
		return other.getType() == types.WILDCARD
	
	def _isEqual(self, other):
		return self._isEquivalent(other)
	
	def _match(self, other, args, kargs):
		args.append(other)
		return other

	def _make(self, args, kargs):
		try:
			return args.pop(0)
		except IndexError:
			raise TypeError('insufficient number of arguments')

	def setAnnotations(self, annotations):
		return self.factory.makeWildcard(annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitWildcard(self, *args, **kargs)


class Variable(Term):
	'''Variable term.'''
	
	def __init__(self, factory, name, pattern, annotations = None):
		Term.__init__(self, factory, annotations)
		self.name = name
		self.pattern = pattern
	
	def getType(self):
		return types.VAR
	
	def _getHash(self):
		return hash((self.name, self.pattern))

	def getName(self):
		return self.name

	def getPattern(self):
		return self.pattern

	def getSymbol(self):
		return self.getName()

	def _isEquivalent(self, other):
		return self.getType() == other.getType() and self.name == other.name and self.pattern.isEquivalent(other.pattern)

	def _isEqual(self, other):
		return self.getType() == other.getType() and self.name == other.name and self.pattern.isEqual(other.pattern)
	
	def isConstant(self):
		return self.pattern.isConstant()
	
	def _match(self, other, args, kargs):
		name = self.getName()
		try:
			value = kargs[name]
			if not kargs[name].isEquivalent(other):
				raise exceptions.PatternMismatchException
			return other
		except KeyError:
			result = self.pattern._match(other, [], kargs)
			kargs[name] = result
			return result

	def _make(self, args, kargs):
		name = self.getName()
		if name in kargs:
			# TODO: do something with the pattern here?
			return kargs[name]
		else:
			raise ValueError('undefined term variable %s' % name)

	def setAnnotations(self, annotations):
		return self.factory.makeVar(self.name, self.pattern, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitVar(self, *args, **kargs)

