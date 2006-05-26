'''Term class hierarchy.'''


# pylint: disable-msg=W0142


from aterm import types
from aterm import exceptions
from aterm import _helpers


class Term(object):
	'''Base class for all terms.'''

	__slots__ = ['factory', 'annotations']
	
	def __init__(self, factory, annotations = None):
		self.factory = factory
		if annotations is None:
			self.annotations = self.factory.makeNil()
		else:
			self.annotations = annotations
	
	def getFactory(self):
		'''Retrieves the factory responsible for creating this Term.'''
		return self.factory
		
	def getType(self):
		'''Gets the type of this term.'''
		return self.type
	
	def getHash(self):
		'''Generate a hash value for this term.'''
		return _helpers.Hash()(self)

	def __hash__(self):
		'''Shorthand for getHash().'''
		return self.getHash()
		
	def isConstant(self):
		'''Whether this term is types, as opposed to have variables or wildcards.'''
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
		'''Shorthand for the isEqual method.'''
		return self.isEqual(other)

	def match(self, other, args = None, kargs = None):
		'''Matches this term agains a string or term pattern.'''
		
		if isinstance(other, basestring):
			other = self.factory.parse(other)
		
		compare = _helpers.PatternComparator(args, kargs)
		return compare(self, other)
	
	def getAnnotation(self, label):
		'''Gets an annotation associated with label'''
		annotations = self.annotations
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
			return self.factory.makeCons(label, self.factory.makeCons(annotation, annotations))
			
		_label = annotations.getHead()
		annotations = annotations.getTail()
		_annotation = annotations.getHead()
		annotations = annotations.getTail()
		
		if label.isEquivalent(_label):
			return self.factory.makeCons(label, self.factory.makeCons(annotation, annotations))
		else:
			return self.factory.makeCons(_label, self.factory.makeCons(_annotation, self._setAnnotation(label, annotation, annotations)))
				
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
			return self.factory.makeCons(_label, self.factory.makeCons(_annotation, self._removeAnnotation(label, annotations)))

	def getAnnotations(self):
		'''Returns the annotation list.'''
		return self.annotations

	def setAnnotations(self, annotations):
		raise NotImplementedError

	#annotations = property(getAnnotations, 'Shorthand for the getAnnotations() method.')
			
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
		return str(self)


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

	def __int__(self):
		return int(self.value)
	
	def setAnnotations(self, annotations):
		return self.factory.makeInt(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitInt(self, *args, **kargs)


class Real(Literal):
	'''Real literal term.'''
	
	__slots__ = []
	
	type = types.REAL
	
	def __float__(self):
		return float(self.value)
	
	def setAnnotations(self, annotations):
		return self.factory.makeReal(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class String(Literal):
	'''String literal term.'''
	
	__slots__ = []
	
	type = types.STR
	
	def setAnnotations(self, annotations):
		return self.factory.makeStr(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class List(Term):
	'''Base class for list terms.'''

	__slots__ = []
	
	type = types.LIST
	
	def isEmpty(self):	
		raise NotImplementedError
	
	def getLength(self):
		raise NotImplementedError
	
	def __len__(self):
		return self.getLength()

	def getHead(self):
		raise NotImplementedError

	def getTail(self):
		raise NotImplementedError

	def __getitem__(self, index):
		if self.isEmpty():
			raise IndexError
		elif index == 0:
			return self.getHead()
		else:
			return self.getTail().__getitem__(index - 1)

	# TODO: write an __iter__ method
		
	def insert(self, element):
		return self.factory.makeCons(element, self)
	
	def append(self, element):
		return self.extend(self.factory.makeConst(element, self.factory.makeNil()))
		
	def extend(self, element):
		raise NotImplementedError
		
	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class Nil(List):
	'''Empty list term.'''
	
	__slots__ = []
	
	def __init__(self, factory, annotations = None):
		# this circular reference must be checked here in order to
		# avoid a infinite loop
		if annotations is None:
			annotations = self
			
		List.__init__(self, factory, annotations)

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		raise exceptions.EmptyListException
	
	def getTail(self):
		raise exceptions.EmptyListException

	def extend(self, tail):
		return tail
		
	def setAnnotations(self, annotations):
		return self.factory.makeNil(annotations)

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

	def _make(self, args, kargs):
		return self.factory.makeCons(
			self.head._make(args, kargs), 
			self.tail._make(args, kargs), 
			self.annotations
		)
	
	def extend(self, tail):
		return self.factory.makeCons(
			self.head, 
			self.tail.append(tail),
			self.getAnnotations()
		)
		
	def setAnnotations(self, annotations):
		return self.factory.makeCons(self.head, self.tail, annotations)

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
	
	def _make(self, args, kargs):
		return self.factory.makeAppl(self.name._make(args, kargs), self.args._make(args, kargs), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeAppl(self.name, self.args, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitAppl(self, *args, **kargs)


class Placeholder(Term):
	'''Base class for placeholder terms.'''

	__slots__ = []
	
	
class Wildcard(Placeholder):
	'''Wildcard term.'''

	__slots__ = []
	
	type = types.WILDCARD
	
	def _make(self, args, kargs):
		try:
			return args.pop(0)
		except IndexError:
			raise TypeError('insufficient number of arguments')

	def setAnnotations(self, annotations):
		return self.factory.makeWildcard(annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitWildcard(self, *args, **kargs)


class Variable(Placeholder):
	'''Variable term.'''
	
	__slots__ = ['name', 'pattern']

	def __init__(self, factory, name, pattern, annotations = None):
		Placeholder.__init__(self, factory, annotations)
		self.name = name
		self.pattern = pattern
	
	type = types.VAR
	
	def getName(self):
		return self.name

	def getPattern(self):
		return self.pattern

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

