'''Term class hierarchy.'''


# pylint: disable-msg=W0142


from aterm import types
from aterm import compare
from aterm import hash
from aterm import annotate
from aterm import write
from aterm import convert
from aterm import lists


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
		return hash.Hash.hash(self)

	def getStructuralHash(self):
		'''Generate a hash value for this term. 
		Annotations are not taken into account.
		'''
		return hash.StructuralHash.hash(self)

	__hash__ = getStructuralHash
		
	def isEquivalent(self, other):
		'''Checks for structural equivalence of this term agains another term.'''
		return compare.isEquivalent(self, other)

	def isEqual(self, other):
		'''Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well.'''
		return compare.isEqual(self, other)
	
	def __eq__(self, other):
		if isinstance(other, Term):
			return compare.isEquivalent(self, other)
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def rmatch(self, other):
		'''Matches this term against a string pattern.'''
		return self.factory.match(other, self)

	def getAnnotations(self):
		'''Returns the annotation list.'''
		if self.annotations is None:
			return self.factory.makeNil()
		else:
			return self.annotations

	def setAnnotations(self, annotations):
		'''Modify the annotation list.'''
		return annotate.annotate(self, annotations)

	def getAnnotation(self, label):
		'''Gets an annotation associated'''
		if not isinstance(label, basestring):
			raise TypeError("label is not a string", label)
		annotations = self.annotations
		while annotations:
			if self.factory.match(label, annotations.head):
				return annotations.head				
			annotations = annotations.tail
		raise ValueError("undefined annotation", label)
	
	def setAnnotation(self, label, annotation):
		'''Returns a new version of this term with the 
		annotation associated with this label added or updated.'''
		if not isinstance(label, basestring):
			raise TypeError("label is not a string", label)
		remover = annotate.Remover(label)
		if self.annotations:
			annotations = remover.visit(self.annotations)
		else:
			annotations = self.factory.makeNil()
		annotations = self.factory.makeCons(annotation, annotations)
		return self.setAnnotations(annotations)
				
	def removeAnnotation(self, label):
		'''Returns a new version of this term with the 
		annotation associated with this label removed.'''
		if not isinstance(label, basestring):
			raise TypeError("label is not a string", label)
		remover = annotate.Remover(label)
		annotation = self.annotations
		if self.annotations:
			annotations = remover.visit(self.annotations)
			return self.setAnnotations(annotations)
		else:
			return self
		
	def accept(self, visitor, *args, **kargs):
		'''Accept a visitor.'''
		raise NotImplementedError

	def writeToTextFile(self, fp):
		'''Write this term to a file object.'''
		writer = write.TextWriter(fp)
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
		try:
			from cStringIO import StringIO
		except ImportError:
			from StringIO import StringIO
		fp = StringIO()
		writer = write.AbbrevTextWriter(fp, 3)
		try:
			writer.visit(self)
		except:
			fp.write('...<error>')
		return '<Term %s>' % (fp.getvalue(),)


class Lit(Term):
	'''Base class for literal terms.'''

	__slots__ = ['value']
	
	def __init__(self, factory, value, annotations = None):
		Term.__init__(self, factory, annotations)
		self.value = value

	def getValue(self):
		return self.value

		
class Integer(Lit):
	'''Integer literal term.'''

	__slots__ = []
	
	type = types.INT

	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, (int, long)):
			raise TypeError('value is not an integer', value)
		Lit.__init__(self, factory, value, annotations)

	def __int__(self):
		return int(self.value)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitInt(self, *args, **kargs)


class Real(Lit):
	'''Real literal term.'''
	
	__slots__ = []
	
	type = types.REAL
	
	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, float):
			raise TypeError('value is not a float', value)
		Lit.__init__(self, factory, value, annotations)

	def __float__(self):
		return float(self.value)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class Str(Lit):
	'''String literal term.'''
	
	__slots__ = []
	
	type = types.STR
	
	def __init__(self, factory, value, annotations = None):
		if not isinstance(value, str):
			raise TypeError('value is not a string', value)
		Lit.__init__(self, factory, value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class List(Term):
	'''Base class for list terms.'''

	__slots__ = []
	
	# Python's list compatability methods
	
	def __nonzero__(self):
		return not lists.empty(self)

	def __len__(self):
		return lists.length(self)

	def __getitem__(self, index):
		return lists.item(self, index)

	def __iter__(self):
		return lists.Iter(self)

	def insert(self, index, element):
		return lists.insert(self, index, element)
	
	def append(self, element):
		return lists.append(self, element)
		
	def extend(self, other):
		return lists.extend(self, other)
	
	def reverse(self):
		return lists.reverse(self)
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class Nil(List):
	'''Empty list term.'''
	
	__slots__ = []

	type = types.NIL
	
	def __init__(self, factory, annotations = None):
		List.__init__(self, factory, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitNil(self, *args, **kargs)


class Cons(List):
	'''Concatenated list term.'''
	
	__slots__ = ['head', 'tail']
	
	type = types.CONS
	
	def __init__(self, factory, head, tail = None, annotations = None):
		List.__init__(self, factory, annotations)
		if not isinstance(head, Term):
			raise TypeError("head is not a term", head)
		self.head = head
		if tail is None:
			self.tail = self.factory.makeNil()
		else:
			if not isinstance(tail, List):
				raise TypeError("tail is not a list term", tail)
			self.tail = tail
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitCons(self, *args, **kargs)


class Appl(Term):
	'''Application term.'''

	__slots__ = ['name', 'args']
	
	type = types.APPL
	
	def __init__(self, factory, name, args = None, annotations = None):
		Term.__init__(self, factory, annotations)
		if not isinstance(name, basestring):
			raise TypeError("name is not a string", name)
		self.name = name
		if args is None:
			self.args = ()
		else:
			self.args = tuple(args)
		for arg in self.args:
			if not isinstance(arg, Term):
				raise TypeError("arg is not a term", arg)			
	
	def getArity(self):
		return len(self.args)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitAppl(self, *args, **kargs)

