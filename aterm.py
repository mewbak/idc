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
		return ATermInt(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		return ATermReal(self, value, annotations)

	def makeAppl(self, afun, args = None, annotations = None):
		return ATermAppl(self, afun, args, annotations)
		
	def makeEmpty(self, annotations = None):
		return ATermListEmpty(self, annotations)

	def makeList(self, head, tail = None, annotations = None):
		return ATermListFilled(self, head, tail, annotations)

	def makePlaceholder(self, placeholder, annotations = None):
		return ATermPlaceholder(self, placeholder, annotations)

	def parse(self, buf):
		from atermLexer import Lexer
		from atermParser import Parser
	
		fp = StringIO(buf)
		lexer = Lexer(fp)
		parser = Parser(lexer, factory = self)
		return parser.aterm()

	

class ATerm(object):
	"""Base class for all ATerms."""

	def __init__(self, factory, annotations = None):
		self.__factory = factory
		self.__annotations = annotations
		
	def getType(self):
		"""Gets the type of this term."""
		raise NotImplementedError

	type = property(lambda self: self.getType(), doc = """The type of this term.""")
	
	def hashCode(self):
		"""Gets a hashcode value of this term."""
		raise NotImplementedError

	def match(self, pattern):
		result = list()
		if self._match(pattern, result):
			return result
		else:
			return None
	
	def _match(self, pattern, result):
		raise NotImplementedError
	
	def getAnnotation(self, label):
		raise NotImplementedError
	
	def setAnnotation(self, label, annotation):
		raise NotImplementedError

	def isEquivalent(self, term):
		raise NotImplementedError
	
	def isEqual(self, other):
		"""Checks equality of this term agains another method.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well."""
		
		if self is other:
			return True
		
		# FIXME: deal with annotations
		if self.isEquivalent(other): 
			return True
		
		return False

	def __eq__(self, other):
		return self.isEqual(other)

	def writeToTextFile(self, fp):
		"""Write this term to a file object."""
		raise NotImplementedError

	def make(self, args):
		"""Create a new term based on this term and a list of arguments."""
		return self
	
	def getFactory(self):
		"""Retrieves the factory responsible for creating this ATerm."""
		return self.__factory
		
	factory = property(getFactory, doc = "The factory responsible for creating this ATerm.""")

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

	value = property(getInt)

	def isEquivalent(self, other):
		return other.type == INT and other.value == self.value
		
	def _match(self, pattern, result):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEquivalent(self.factory.intPattern):
			result.append(self)
			return True
		
		return False
	
	def setAnnotations(self, annotations):
		self.factory.makeInt(self.value, annotations)

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
		return other.type == REAL and other.value == self.value

	def getReal(self):
		return self.__value

	value = property(getReal)
		
	def _match(self, pattern, result):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEquivalent(self.factory.realPattern):
			result.append(self)
			return True
		
		return False
	
				
	def setAnnotations(self, annotations):
		self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		visitor.visitInt(self)
	
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
		if other.type != APPL:
			return False
		
		if other.afun != self.afun:
			return False
		
		if len(other.args) != len(self.args):
			return False
		
		for self_arg, other_arg in zip(self.args, other.args):
			if not other_arg.isEquivalent(self_arg):
				return False
		
		return True

	def _match(self, pattern, result):
		if pattern.type == APPL:
			if pattern.fun == self.fun:
				return self._matchArguments(pattern.arguments, result)
			else:
				return False

		# XXX:
		if pattern.type == PLACEHOLDER:
			if pattern.placeholder.type == APPL:
				pass
		
		return False
			
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

	def _match(self, pattern, result):
		return pattern.isEquivalent(self) or pattern.isEquivalent(self.factory.listPattern)

	def insert(self, element):
		return self.factory.makeList(element, self)
		
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
		return other.type == LIST and other.getLength == 0

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
		return other.type == LIST and not other.isEmpty() and other.head.isEquivalent(self.head) and other.tail.isEquivalent(self.tail)
		
	def setAnnotations(self, annotations):
		return self.factory.makeList(self.head, self.tail, annotations)


class ATermPlaceholder(ATerm):

	def __init__(self, factory, placeholder, annotations = None):
		ATerm.__init__(self, factory, annotations)
		
		self.placeholder = placeholder
		
	def getType(self):
		return PLACEHOLDER
	
	def isEquivalent(self, other):
		return other.type == PLACEHOLDER and other.placeholder == self.placeholder
	
	def _match(self, pattern):
		return pattern.isEquivalent(self) or pattern.isEquivalent(self.factory.placeholderPattern)
	
	def writeToTextFile(self, fp):
		fp.write('<')
		self.type.writeToTextFile(fp)
		fp.write('>')


class ATermBlob(ATerm):

	# TODO: implement this

	pass
