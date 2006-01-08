'''Python version of the ATerm library. Loosely based on the Java version.'''


try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

from atermLexer import Lexer
from atermParser import Parser	


# Term types
INT = 1
REAL = 2
STR = 3
LIST = 4
APPL = 5
PLACEHOLDER = 6
BLOB = 7


class Factory(object):
	'''An Factory is responsible for make new ATerms, either by parsing 
	from string or stream, or via one the of the "make" methods.'''

	def __init__(self):
		self.intPattern = self.makePlaceholder(self.makeAppl('int'))
		self.realPattern = self.makePlaceholder(self.makeAppl('real'))
		self.strPattern = self.makePlaceholder(self.makeAppl('str'))
		self.applPattern = self.makePlaceholder(self.makeAppl('appl'))
		self.funPattern = self.makePlaceholder(self.makeAppl('fun'))
		self.listPattern = self.makePlaceholder(self.makeAppl('list'))				
		self.termPattern = self.makePlaceholder(self.makeAppl('term'))			
		self.placeholderPattern = self.makePlaceholder(self.makeAppl('placeholder'))
		
		self.parseCache = {}

	def makeInt(self, value, annotations = None):
		'''Creates a new IntATerm object'''
		return IntATerm(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		'''Creates a new RealATerm object'''
		return RealATerm(self, value, annotations)

	def makeStr(self, value, annotations = None):
		'''Creates a new StrATerm object'''
		return StrATerm(self, value, annotations)

	def makeAppl(self, name, args = None, annotations = None):
		'''Creates a new ApplATerm object'''
		return ApplATerm(self, name, args, annotations)
		
	def makeEmpty(self, annotations = None):
		'''Creates an empty ListATerm object'''
		return EmptyListATerm(self, annotations)

	def makeList(self, head, tail = None, annotations = None):
		'''Creates a new ListATerm object'''
		return FilledListATerm(self, head, tail, annotations)

	def makePlaceholder(self, placeholder, annotations = None):
		'''Creates a new PlaceholderATerm object'''
		return PlaceholderATerm(self, placeholder, annotations)

	def readFromTextFile(self, fp):
		'''Creates a new ATerm by parsing from a text stream.'''
		lexer = Lexer(fp)
		parser = Parser(lexer, factory = self)
		# TODO: catch exceptions
		return parser.aterm()
	
	def parse(self, buf):
		'''Creates a new ATerm by parsing a string.'''

		try:
			return self.parseCache[buf]
		except KeyError:
			fp = StringIO(buf)
			result = self.readFromTextFile(fp)
			self.parseCache[buf] = result
			return result

	def make(self, pattern, *args):
		'''Creates a new ATerm from a string pattern and a list of arguments. 
		First the string pattern is parsed into an ATerm. Then the holes in 
		the pattern are filled with arguments taken from the supplied list of 
		arguments.'''
		return self.parse(pattern).make(*args)


class ATerm(object):
	'''Base class for all ATerms.'''

	def __init__(self, factory, annotations = None):
		self.factory = factory		
		self.__annotations = annotations

	def getFactory(self):
		'''Retrieves the factory responsible for creating this ATerm.'''
		return self.factory
		
	def getType(self):
		'''Gets the type of this term.'''
		raise NotImplementedError

	type = property(lambda self: self.getType(), doc = '''Shorthand for type of this term.''')

	def isEquivalent(self, term):
		'''Checks for structural equivalence of this term agains another term.'''
		raise NotImplementedError
		
	def match(self, pattern, matches = None):
		'''Matches this term agains a string or term pattern.'''
		
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
		'''Gets an annotation associated with label'''
		raise NotImplementedError
	
	def setAnnotation(self, label, annotation):
		'''Returns a new version of this term with the 
		annotation associated with this label added or updated.'''
		raise NotImplementedError

	def removeAnnotation(self, label):
		'''Returns a new version of this term with the 
		annotation associated with this label removed.'''
		raise NotImplementedError

	def getAnnotations(self):
		if self.__annotations is None:
			return self.factory.makeEmpty()
		else:
			return self.__annotations
	
	annotations = property(getAnnotations, doc = '''Shorthand for the getAnnotations method.''')
	
	def isEqual(self, other):
		'''Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well.'''
		raise NotImplementedError

	def __eq__(self, other):
		'''Shorthand for the isEqual method.'''
		return self.isEqual(other)

	def make(self, *args):
		'''Create a new term based on this term and a list of arguments.'''
		return self._make(list(args))

	def _make(self, args):
		return self

	def accept(self, visitor):
		raise NotImplementedError

	def writeToTextFile(self, fp):
		'''Write this term to a file object.'''
		writer = TextWriter(fp)
		writer.visit(self)

	def __str__(self):
		'''Get the string representation of this term.'''
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()
	
	def __repr__(self):
		return str(self)


class LiteralATerm(ATerm):

	def __init__(self, factory, value, annotations = None):
		ATerm.__init__(self, factory, annotations)
		self.__value = value

	def getValue(self):
		return self.__value

	value = property(getValue, doc = '''Shorthand for the integer value.''')

	def isEquivalent(self, other):
		return other is self or (other.type == self.type and other.value == self.value)

	def isEqual(self, other):
		return other is self or (other.type == self.type and other.value == self.value) and self.annotations.isEquivalent(other.annotations)

	def _match(self, pattern, matches):
		if pattern.isEquivalent(self):
			return True
		
		if pattern.isEquivalent(self.getPattern()):
			matches.append(self.getValue())
			return True
		
		return super(LiteralATerm, self)._match(pattern, matches)

	def getPattern(self):
		raise NotImplementedError


class IntATerm(LiteralATerm):

	def getType(self):
		return INT

	def getPattern(self):
		return self.factory.intPattern
	
	def setAnnotations(self, annotations):
		return self.factory.makeInt(self.value, annotations)

	def accept(self, visitor):
		visitor.visitInt(self)


class RealATerm(LiteralATerm):

	def getType(self):
		return REAL

	def getPattern(self):
		return self.factory.realPattern
	
	def setAnnotations(self, annotations):
		return self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		visitor.visitReal(self)


class StrATerm(LiteralATerm):

	def getType(self):
		return STR

	def getPattern(self):
		return self.factory.strPattern
	
	def setAnnotations(self, annotations):
		return self.factory.makeStr(self.value, annotations)

	def accept(self, visitor):
		visitor.visitStr(self)

	
class ApplATerm(ATerm):

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
		
		if pattern.type == PLACEHOLDER and pattern.placeholder.type == APPL and pattern.placeholder.name == 'fun':
			matches.append(self.name)
			return self.args._match(pattern.placeholder.args, matches)
		
		return super(ApplATerm, self)._match(pattern, matches)
	
	def _make(self, args):
		return self.factory.makeAppl(self.name, self.args._make(args), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeAppl(self.name, self.args, annotations)

	def accept(self, visitor):
		visitor.visitAppl(self)


class ListATerm(ATerm):

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


class EmptyListATerm(ListATerm):
	
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
		
		return super(EmptyListATerm, self)._match(pattern, matches)

	def setAnnotations(self, annotations):
		return self.factory.makeEmpty(annotations)


class FilledListATerm(ListATerm):

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
		
		return super(FilledListATerm, self)._match(pattern, matches)

	def _make(self, args):
		if self.head.isEquivalent(self.factory.listPattern) and self.tail.isEmpty:
			arg = args.pop(0)
			if not isinstance(arg, ListATerm):
				raise TypeError, 'not an aterm list: ' + repr(arg)
			return arg
		else:
			return self.factory.makeList(self.head._make(args), self.tail._make(args), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeList(self.head, self.tail, annotations)


class PlaceholderATerm(ATerm):

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
		
		return super(PlaceholderATerm, self)._match(pattern, matches)

	def _make(self, args):
		if self.placeholder.type == APPL:
			name = self.placeholder.name
			if name == 'appl':
				arg = args.pop(0)
				if not isinstance(arg, basestring):
					raise TypeError, 'not a string: ' + repr(arg)
				return self.factory.makeAppl(arg, self.placeholder.getArgs()._make(args), self.annotations)
			elif self.placeholder.getArity() == 0:
				if name == 'int':
					arg = args.pop(0)
					if not isinstance(arg, int):
						raise TypeError, 'not an integer: ' + repr(arg)
					return self.factory.makeInt(arg, self.annotations)
				elif name == 'real':
					arg = args.pop(0)
					if not isinstance(arg, float):
						raise TypeError, 'not an floating point number: ' + repr(arg)
					return self.factory.makeReal(arg, self.annotations)
				elif name == 'str':
					arg = args.pop(0)
					if not isinstance(arg, basestring):
						raise TypeError, 'not a string: ' + repr(arg)
					return self.factory.makeStr(arg, self.annotations)
				elif name == 'placeholder':
					arg = args.pop(0)
					if not isinstance(arg, ATerm):
						raise TypeError, 'not an aterm: ' + repr(arg)
					return self.factory.makePlaceholder(arg, self.annotations)
				elif name == 'term':
					arg = args.pop(0)
					if not isinstance(arg, ATerm):
						raise TypeError, 'not an aterm: ' + repr(arg)
					return arg
		
		raise ValueError, 'illegal pattern: ' + str(self)		
		
	def setAnnotations(self, annotations):
		return self.factory.makePlaceholder(self.placeholder, annotations)

	def accept(self, visitor):
		visitor.visitPlaceholder(self)


class BlobATerm(ATerm):

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

	def visitStr(self, term):
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
		self.fp.write('%.2g' % rterm.getValue())
		self.writeAnnotations(rterm)
	
	def visitStr(self, sterm):
		self.fp.write('"%r"' % sterm.getValue())
		self.writeAnnotations(sterm)
	
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
