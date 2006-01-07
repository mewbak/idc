"""Python version of the ATerm library. Loosely based on the Java version."""


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
name = 7


class ATermFactory(object):
	"""An ATermFactory is responsible for make new ATerms, either by parsing 
	from string or stream, or via one the of the "make" methods."""

	def __init__(self):
		self.intPattern = self.makePlaceholder(self.makeAppl("int"))
		self.realPattern = self.makePlaceholder(self.makeAppl("real"))
		self.applPattern = self.makePlaceholder(self.makeAppl("appl"))
		self.listPattern = self.makePlaceholder(self.makeAppl("list"))				
		self.termPattern = self.makePlaceholder(self.makeAppl("term"))				
		self.placeholderPattern = self.makePlaceholder(self.makeAppl("placeholder"))				

	def makeInt(self, value, annotations = None):
		"""Creates a new ATermInt object"""
		return ATermInt(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		"""Creates a new ATermReal object"""
		return ATermReal(self, value, annotations)

	def makeAppl(self, name, args = None, annotations = None):
		"""Creates a new ATermAppl object"""
		return ATermAppl(self, name, args, annotations)
		
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
		self.factory = factory		
		self.__annotations = annotations

	def getFactory(self):
		"""Retrieves the factory responsible for creating this ATerm."""
		return self.factory
		
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
		if pattern.isEquivalent(self.factory.termPattern):
			matches.append(self)
			return True
		
		return False

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
	
	annotations = property(getAnnotations, doc = """Shorthand for the getAnnotations method.""")
	
	def isEqual(self, other):
		"""Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well."""
		raise NotImplementedError

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
		writer = TextWriter(fp)
		writer.visit(self)

	def __str__(self):
		"""Get the string representation of this term."""
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()
	
	def __repr__(self):
		return str(self)


class ATermLiteral(ATerm):

	def __init__(self, factory, value, annotations = None):
		ATerm.__init__(self, factory, annotations)
		self.__value = value

	def getValue(self):
		return self.__value

	value = property(getValue, doc = """Shorthand for the integer value.""")

	def isEquivalent(self, other):
		return other is self or (other.type == self.type and other.value == self.value)

	def isEqual(self, other):
		return other is self or (other.type == self.type and other.value == self.value) and self.annotations.isEquivalent(other.annotations)

		

class ATermInt(ATermLiteral):

	def getType(self):
		return INT

	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEquivalent(self.factory.intPattern):
			matches.append(self)
			return True
		
		return super(ATermInt, self)._match(pattern, matches)

	def setAnnotations(self, annotations):
		return self.factory.makeInt(self.value, annotations)

	def accept(self, visitor):
		visitor.visitInt(self)


class ATermReal(ATermLiteral):

	def getType(self):
		return REAL

	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEquivalent(self.factory.realPattern):
			matches.append(self)
			return True
		
		return super(ATermReal, self)._match(pattern, matches)

	def setAnnotations(self, annotations):
		return self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		visitor.visitReal(self)

	
class ATermAppl(ATerm):

	def __init__(self, factory, name, args = None, annotations = None):
		ATerm.__init__(self, factory, annotations)

		self.name = name
		if args is None:
			self.args = self.factory.makeEmpty()
		else:
			self.args = args
	
	def getType(self):
		return APPL

	def getName(self):
		return self.name
	
	def getArity(self):
		return self.args.getLength()

	def getArgs(self):
		return self.args
	
	def isEquivalent(self, other):
		return other is self or (other.type == APPL and other.name == self.name and other.args.isEquivalent(self.args))

	def isEqual(self, other):
		return other is self or (other.type == APPL and other.name == self.name and other.args.isEqual(self.args) and other.annotations.isEquivalent(self.annotations))
		
	def _match(self, pattern, matches):
		if pattern is self:
			return True
		
		if pattern.type == APPL:
			return self.name == pattern.name and self.args._match(pattern.args, matches)
		
		if pattern.isEquivalent(self.factory.applPattern):
			matches.append(self)
			return True
		
		return super(ATermAppl, self)._match(pattern, matches)
	
	def setAnnotations(self, annotations):
		return self.factory.makeAppl(self.name, self.args, annotations)

	def accept(self, visitor):
		visitor.visitAppl(self)



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

	def insert(self, element):
		return self.factory.makeList(element, self)
	
	def accept(self, visitor):
		visitor.visitList(self)


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
		return other is self or (other.type == LIST and other.isEmpty())

	def isEqual(self, other):
		return self.isEquivalent(other) and self.annotations.isEquivalent(other)

	def _match(self, pattern, matches):
		if self is pattern:
			return True
		
		if pattern.type == LIST:
			if pattern.isEmpty():
				return True
			elif pattern.head.isEquivalent(self.factory.listPattern):
				matches.append(self)
				return True
		
		return super(ATermListEmpty, self)._match(pattern, matches)

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
	
	def getHead(self):
		return self.head
	
	def getTail(self):
		return self.tail

	def isEquivalent(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEquivalent(self.head) and other.tail.isEquivalent(self.tail))
		
	def isEqual(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEqual(self.head) and other.tail.isEqual(self.tail)) and self.annotations.isEquivalent(other.annotations)
	
	def _match(self, pattern, matches):
		if self is pattern:
			return True
		
		if pattern.type == LIST:
			if not pattern.isEmpty():
				if self.head._match(pattern.head, matches):
					return self.tail._match(pattern.tail, matches)
				elif pattern.head.isEquivalent(self.factory.listPattern):
					matches.append(self)
					return True
		
		return super(ATermListFilled, self)._match(pattern, matches)

	def setAnnotations(self, annotations):
		return self.factory.makeList(self.head, self.tail, annotations)


class ATermPlaceholder(ATerm):

	def __init__(self, factory, placeholder, annotations = None):
		ATerm.__init__(self, factory, annotations)
		
		self.placeholder = placeholder
		
	def getType(self):
		return PLACEHOLDER
	
	def getPlaceholder(self):
		return self.placeholder
	
	def isEquivalent(self, other):
		return other is self or (other.type == PLACEHOLDER and other.placeholder.isEquivalent(self.placeholder))
	
	def isEqual(self, other):
		return other is self or (other.type == PLACEHOLDER and other.placeholder.isEqual(self.placeholder) and other.annotations.isEquivalent(self.annotations)) 
	
	def _match(self, pattern, matches):
		if pattern.isEquivalent(self.factory.placeholderPattern):
			matches.append(self)
			return True
		
		return super(ATermPlaceholder, self)._match(pattern, matches)

	def setAnnotations(self, annotations):
		return self.factory.makePlaceholder(self.placeholder, annotations)

	def accept(self, visitor):
		visitor.visitPlaceholder(self)


class ATermBlob(ATerm):

	# TODO: implement this

	pass


class Visitor(object):
	
	def visit(self, term):
		assert isinstance(term, ATerm)
		term.accept(self)

	def visitATerm(self, term):
		pass

	def visitInt(self, term):
		self.visitATerm(self, term)

	def visitReal(self, term):
		self.visitATerm(self, term)

	def visitAppl(self, term):
		self.visitATerm(self, term)

	def visitList(self, term):
		self.visitATerm(self, term)

	def visitBlob(self, term):
		self.visitATerm(self, term)


class TextWriter(Visitor):
	
	def __init__(self, fp):
		self.fp = fp
	
	def writeTerms(self, terms):
		#self.visit(terms[0])
		#for term in terms[1:]:
		#	self.fp.write(',')
		#	self.visit(term)
		assert isinstance(terms, ATermList)
		if not terms.isEmpty():
			self.visit(terms.head)
			terms = terms.tail
			while not terms.isEmpty():
				self.fp.write(',')
				self.visit(terms.head)
				terms = terms.tail

	def writeAnnotations(self, term):
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			self.fp.write('{')
			self.writeTerms(annotations)
			self.fp.write('}')

	def visitInt(self, iterm):
		self.fp.write(str(iterm.getValue()))
		self.writeAnnotations(iterm)
	
	def visitReal(self, rterm):
		self.fp.write("%.15e" % rterm.getValue())
		self.writeAnnotations(rterm)
	
	def visitAppl(self, aterm):
		self.fp.write(aterm.getName())
		if aterm.getArity():
			self.fp.write('(')
			self.writeTerms(aterm.getArgs())
			self.fp.write(')')
		self.writeAnnotations(aterm)
	
	def visitList(self, lterm):
		self.fp.write('[')
		self.writeTerms(lterm)			
		self.fp.write(']')

	def visitPlaceholder(self, pterm):
		self.fp.write('<')
		self.visit(pterm.getPlaceholder())
		self.fp.write('>')
