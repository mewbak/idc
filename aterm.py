"""Python version of the ATerm library. Based on the Java version."""


try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO
	

# Term types
INT = 1
REAL = 2
APPL = 3
LIST = 4
PLACEHOLDER = 5
BLOB = 6
AFUN = 7


class ATermFactory(object):

	def __init__(self):
		self.intPattern = self.makePlaceholder(self.makeAppl("int"))
		self.realPattern = self.makePlaceholder(self.makeAppl("real"))
		self.applPattern = self.makePlaceholder(self.makeAppl("appl"))
		self.listPattern = self.makePlaceholder(self.makeAppl("list"))				
		self.placeholderPattern = self.makePlaceholder(self.makeAppl("placeholder"))				

	def makeInt(self, value, annotations = None):
		"""Creates a new ATermInt object"""
		return ATermInt(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		"""Creates a new ATermReal object"""
		return ATermReal(self, value, annotations)

	def makeAppl(self, afun, args = None, annotations = None):
		"""Creates a new ATermAppl object"""
		return ATermAppl(self, afun, args, annotations)
		
	def makeEmpty(self, annotations = None):
		"""Creates an empty ATermList object"""
		return ATermListEmpty(self, annotations)

	def makeList(self, head, tail = None, annotations = None):
		"""Creates a new ATermList object"""
		return ATermListFilled(self, head, tail, annotations)

	def makePlaceholder(self, placeholder, annotations = None):
		"""Creates a new ATermPlaceholder object"""
		return ATermPlaceholder(self, placeholder, annotations)

	def readFromTextFile(self, fp):
		"""Creates a new ATerm by parsing from a text stream."""
		from atermLexer import Lexer
		from atermParser import Parser
	
		lexer = Lexer(fp)
		parser = Parser(lexer, factory = self)
		# TODO: catch exceptions
		return parser.aterm()
	
	def parse(self, buf):
		"""Creates a new ATerm by parsing a string."""
		fp = StringIO(buf)
		return self.readFromTextFile(fp)

	def make(self, pattern, args):
		"""Creates a new ATerm from a string pattern and a list of arguments. 
		First the string pattern is parsed into an ATerm. Then the holes in 
		the pattern are filled with arguments taken from the supplied list of 
		arguments."""
		return self.parse(pattern).make(args)



class ATerm(object):
	"""Base class for all ATerms."""

	def __init__(self, factory, annotations = None):
		self.__factory = factory		
		self.__annotations = annotations

	def getFactory(self):
		"""Retrieves the factory responsible for creating this ATerm."""
		return self.__factory
		
	factory = property(getFactory, doc = "The factory responsible for creating this ATerm.""")

	def getType(self):
		"""Gets the type of this term."""
		raise NotImplementedError

	type = property(lambda self: self.getType(), doc = """Shorthand for type of this term.""")

	def isEquivalent(self, term):
		"""Checks for structural equivalence of this term agains another term."""
		raise NotImplementedError
		
	def match(self, pattern, matches = None):
		"""Matches this term agains a string or term pattern."""
		
		if isinstance(pattern, basestring):
			pattern = self.factory.parse(pattern)
		
		if matches is None:
			matches = []
		
		return self._match(pattern, matches)
	
	def _match(self, pattern, matches):
		raise NotImplementedError
	
	def getAnnotation(self, label):
		"""Gets an annotation associated with label"""
		raise NotImplementedError
	
	def setAnnotation(self, label, annotation):
		"""Returns a new version of this term with the 
		annotation associated with this label added or updated."""
		raise NotImplementedError

	def removeAnnotation(self, label):
		"""Returns a new version of this term with the 
		annotation associated with this label removed."""
		raise NotImplementedError

	def getAnnotations(self):
		if self.__annotations is None:
			return self.factory.makeEmpty()
		else:
			return self.__annotations
	
	annotations = property(getAnnotations, doc = """Shorthand for getAnnotations.""")
	
	def isEqual(self, other):
		"""Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well."""
		
		if self is other:
			return True
		
		# FIXME: deal with annotations
		if self.isEquivalent(other):
			if self.__annotations is None:
				return other.__annotations is None
			else:
				return self.__annotations.isEquivalent(other.__annotations) 
		
		return False

	def __eq__(self, other):
		"""Shorthand for the isEqual method."""
		return self.isEqual(other)

	def make(self, args):
		"""Create a new term based on this term and a list of arguments."""
		return self

	def accept(self, visitor):
		raise NotImplementedError

	def writeToTextFile(self, fp):
		"""Write this term to a file object."""
		raise NotImplementedError

	def __str__(self):
		"""Get the string representation of this term."""
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()


class ATermInt(ATerm):

	def __init__(self, factory, value, annotations = None):
		ATerm.__init__(self, factory, annotations)
		self.__value = value

	def getType(self):
		return INT

	def getInt(self):
		return self.__value

	value = property(getInt, doc = """Shorthand for the integer value.""")

	def isEquivalent(self, other):
		return other is self or (other.type == INT and other.__value == self.__value)
		
	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEqual(self.factory.intPattern):
			matches.append(self)
			return True
		
		return False
	
	def setAnnotations(self, annotations):
		self.factory.makeInt(self.__value, annotations)

	def accept(self, visitor):
		visitor.visitInt(self)
	
	def writeToTextFile(self, fp):
		fp.write("%d" % self.value)


class ATermReal(ATerm):

	def __init__(self, factory, value, annotations = None):
		ATerm.__init__(self, factory, annotations)
		self.__value = value

	def getType(self):
		return REAL

	def isEquivalent(self, other):
		return other is self or (other.type == REAL and other.value == self.value)

	def getReal(self):
		return self.__value

	value = property(getReal)
		
	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEqual(self.factory.realPattern):
			matches.append(self)
			return True
		
		return False

	def setAnnotations(self, annotations):
		self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		visitor.visitReal(self)
	
	def writeToTextFile(self, fp):
		fp.write("%.15e" % self.value)
	
	
class ATermAppl(ATerm):

	def __init__(self, factory, afun, args = None, annotations = None):
		ATerm.__init__(self, factory, annotations)

		self.afun = afun
		if args is None:
			self.args = self.factory.makeEmpty()
		else:
			self.args = args
	
	def getType(self):
		return APPL

	def getArity(self):
		return self.args.getLength()

	def isEquivalent(self, other):
		return other is self or (other.type == APPL and other.afun == self.afun and other.args.isEquivalent(self.args))

	def isEqual(self, other):
		return other is self or (other.type == APPL and other.afun == self.afun and other.args.isEqual(self.args) and other.annotations.isEqual(self.annotations))
		
	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEqual(self.factory.applPattern):
			matches.append(self)
			return True
		
		return False
	
	def visit(self, visitor):
		visitor.visitAppl(self)
	
	def writeToTextFile(self, fp):
		if self.sym:
			fp.write(self.sym)
		if self.arity():
			fp.write('(')
			self.args[0].writeToTextFile(fp)
			for arg in self.args[1:]:
				fp.write(',')
				arg.writeToTextFile(fp)
			fp.write(')')


class ATermList(ATerm):

	def getType(self):
		return LIST

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

	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEqual(self.factory.listPattern):
			matches.append(self)
			return True
		
		return False

	def insert(self, element):
		return self.factory.makeList(element, self)
	
	def visit(self, visitor):
		visitor.visitList(self)
		
	def writeToTextFile(self, fp):
		fp.write('[')
		if not self.isEmpty():
			self.head.writeToTextFile(fp)
			tail = self.tail
			while not tail.isEmpty():
				fp.write(',')
				tail.head.writeToTextFile(fp)
				tail = tail.tail
		fp.write(']')

class ATermListEmpty(ATermList):
	
	def __init__(self, factory, annotations = None):
		ATerm.__init__(self, factory, annotations)

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		return None
	
	def getTail(self):
		return None

	def isEquivalent(self, other):
		return other.type == LIST and other.getLength() == 0

	def setAnnotations(self, annotations):
		return self.factory.makeEmpty(annotations)


class ATermListFilled(ATermList):

	def __init__(self, factory, head, tail = None, annotations = None):
		ATerm.__init__(self, factory, annotations)

		self.head = head
		if tail is None:
			self.tail = self.factory.makeEmpty()
		else:
			self.tail = tail
	
	def isEmpty(self):
		return False
	
	def getLength(self):
		return 1 + self.tail.getLength()
	
	def isEquivalent(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEquivalent(self.head) and other.tail.isEquivalent(self.tail))
		
	def isEqual(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEqual(self.head) and other.tail.isEqual(self.tail))
		
	def setAnnotations(self, annotations):
		return self.factory.makeList(self.head, self.tail, annotations)


class ATermPlaceholder(ATerm):

	def __init__(self, factory, placeholder, annotations = None):
		ATerm.__init__(self, factory, annotations)
		
		self.placeholder = placeholder
		
	def getType(self):
		return PLACEHOLDER
	
	def isEquivalent(self, other):
		return other is self or (other.type == PLACEHOLDER and other.placeholder.isEquivalent(self.placeholder))
	
	def isEqual(self, other):
		return other is self or (other.type == PLACEHOLDER and other.placeholder.isEqual(self.placeholder) and other.annotations.isEqual(self.annotations)) 
	
	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEqual(self.factory.placeholderPattern):
			matches.append(self)
			return True
		
		return False

	def visit(self, visitor):
		visitor.visitPlaceholder(self)
		
	def writeToTextFile(self, fp):
		fp.write('<')
		self.type.writeToTextFile(fp)
		fp.write('>')


class ATermBlob(ATerm):

	# TODO: implement this

	pass
