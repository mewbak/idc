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

	def makeInt(self, value, annotations = None):
		return ATermInt(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		return ATermReal(self, value, annotations)

	def makeList(self, head = None, tail = None):
		# XXX:
		pass

	def makeAppl(self, afun, args = (), annotations = None):
		return ATermAppl(self, afun, args, annotations)
		
	def makePlaceholder(self, type, annotations = None):
		return ATermPlaceholder(self, fun, args, annotations)

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
		if self._match(self, pattern):
			return result
		else:
			return None
	
	def _match(self, pattern, result):
		raise NotImplementedError
	
	def getAnnotation(self, label):
		raise NotImplementedError
	
	def setAnnotation(self, label, annotation):
		raise NotImplementedError
		
	def isEqual(self, term):
		"""Checks equality of this term agains another method.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well."""
		
		if self is term:
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

	def _match(self, pattern, result):
		if self == pattern:
			return True

		if pattern.type == PLACEHOLDER:
			if pattern.placeholder.type == APPL:
				afun = pattern.placeholder.afun
				if afun.name == "int" and afun.arity == 0: # XXX: quoted not respected
					result.append(self.value)
					return True
				
		return False
				
	def getInt(self):
		return self.__value

	value = property(getInt)

	def setAnnotations(annotations):
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

	def _match(self, pattern, result):
		if self == pattern:
			return True

		if pattern.type == PLACEHOLDER:
			if pattern.placeholder.type == APPL:
				afun = pattern.placeholder.afun
				if afun.name == "real" and afun.arity == 0: # XXX: quoted not respected
					result.append(self.value)
					return True
				
		return False
				
	def getReal(self):
		return self.__value

	value = property(getReal)

	def setAnnotations(annotations):
		self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		visitor.visitInt(self)
	
	def writeToTextFile(self, fp):
		fp.write("%.15e" % self.value)
	
	
class ATermAppl(ATerm):

	def __init__(self, factory, afun, args = (), annotations = None):
		ATerm.__init__(self, factory, annotations)

		self.afun = afun
		self.args = args
	
	def getType(self):
		return APPL
			
	def getArity(self):
		return len(self.args)

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

	def __init__(self, elements):
		self.elements = elements
	
	def writeToTextFile(self, fp):
		fp.write('[')
		if len(self.elements):
			self.elements[0].writeToTextFile(fp)
			for element in self.elements[1:]:
				fp.write(',')
				element.writeToTextFile(fp)
		fp.write(']')


class ATermPlaceholder(ATerm):

	def __init__(self, type):
		self.type = type

	def writeToTextFile(self, fp):
		fp.write('<')
		self.type.writeToTextFile(fp)
		fp.write('>')


class ATermBlob(ATerm):

	# XXX:

	pass


