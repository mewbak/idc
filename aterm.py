'''Module for term representation and manipulation. Loosely inspired on the Java
version of the ATerm library.'''

# TODO: maximal sharing
# TODO: annotations

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
CONS = 5
VAR = 6
APPL = 7
WILDCARD = 8


class Factory(object):
	'''An Factory is responsible for make new Terms, either by parsing 
	from string or stream, or via one the of the "make" methods.'''

	MAX_PARSE_CACHE_LEN = 512
	
	def __init__(self):
		self.parseCache = {}

	def makeInt(self, value, annotations = None):
		'''Creates a new integer literal term'''
		return Integer(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		'''Creates a new real literal term'''
		return Real(self, value, annotations)

	def makeStr(self, value, annotations = None):
		'''Creates a new string literal term'''
		return String(self, value, annotations)

	def makeCons(self, name, annotations = None):
		'''Creates a new constructor term'''
		return Constructor(self, name, annotations)

	def makeVar(self, name, annotations = None):
		'''Creates a new variable term'''
		return Variable(self, name, annotations)

	def makeWildcard(self, annotations = None):
		'''Creates a new wildcard term'''
		return Wildcard(self, annotations)

	def makeNilList(self, annotations = None):
		'''Creates a new empty list term'''
		return _NilList(self, annotations)

	def makeConsList(self, head, tail = None, annotations = None):
		'''Creates a new extended list term'''
		return _ConsList(self, head, tail, annotations)

	def makeList(self, seq, annotations = None):
		res = self.makeNilList()
		for i in range(len(seq)-1,-1,-1):
			res = self.makeConsList(seq[i], res)
		if annotations is not None:
			res = res.setAnnotations(annotations)
		return res
		
	def makeAppl(self, name, args = None, annotations = None):
		'''Creates a new appplication term'''
		return Application(self, name, args, annotations)

	def readFromTextFile(self, fp):
		'''Creates a new term by parsing from a text stream.'''
		lexer = Lexer(fp)
		parser = Parser(lexer, factory = self)
		# TODO: catch exceptions
		return parser.term()
	
	def parse(self, buf):
		'''Creates a new term by parsing a string.'''

		try:
			return self.parseCache[buf]
		except KeyError:
			fp = StringIO(buf)
			result = self.readFromTextFile(fp)
			
			if len(self.parseCache) > self.MAX_PARSE_CACHE_LEN:
				# TODO: use a LRU cache policy
				self.parseCache.clear()
			self.parseCache[buf] = result
			
			return result

	def make(self, pattern, vars):
		'''Creates a new term from a string pattern and a list of arguments. 
		First the string pattern is parsed into an Term. Then the holes in 
		the pattern are filled with arguments taken from the supplied list of 
		arguments.'''
		return self.parse(pattern).make(vars)


class Term(object):
	'''Base class for all Terms.'''

	def __init__(self, factory, annotations = None):
		self.factory = factory		
		self.__annotations = annotations

	def getFactory(self):
		'''Retrieves the factory responsible for creating this Term.'''
		return self.factory
		
	def getType(self):
		'''Gets the type of this term.'''
		raise NotImplementedError

	type = property(lambda self: self.getType(), doc = '''Shorthand for type of this term.''')

	def isConstant(self):
		raise NotImplementedError
	
	def isEquivalent(self, term):
		'''Checks for structural equivalence of this term agains another term.'''
		raise NotImplementedError
		
	def match(self, other, vars = None):
		'''Matches this term agains a string or term pattern.'''
		
		if isinstance(other, basestring):
			pattern = self.factory.parse(other)
		
		if vars is None:
			vars = {}
		
		return self._match(other, vars)
	
	def _match(self, other, vars):
		return False

	# FIxME: annotations are not fully impletemented
	
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
			return self.factory.makeNilList()
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

	def make(self, vars):
		'''Create a new term based on this term and a list of arguments.'''
		return self._make(vars)

	def _make(self, vars):
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


class Literal(Term):

	def __init__(self, factory, value, annotations = None):
		Term.__init__(self, factory, annotations)
		self.__value = value

	def getValue(self):
		return self.__value

	value = property(getValue, doc = '''Shorthand for the integer value.''')

	def isConstant(self):
		return True
	
	def isEquivalent(self, other):
		return other is self or (other.type == self.type and other.value == self.value)

	def isEqual(self, other):
		return other is self or (other.type == self.type and other.value == self.value) and self.annotations.isEquivalent(other.annotations)

	def _match(self, other, vars):
		if other.isEquivalent(self):
			return True
		
		return Term._match(self, other, vars)

	def getPattern(self):
		raise NotImplementedError


class Integer(Literal):

	def getType(self):
		return INT

	def setAnnotations(self, annotations):
		return self.factory.makeInt(self.value, annotations)

	def accept(self, visitor):
		return visitor.visitInt(self)


class Real(Literal):

	def getType(self):
		return REAL

	def setAnnotations(self, annotations):
		return self.factory.makeReal(self.value, annotations)

	def accept(self, visitor):
		return visitor.visitReal(self)


class String(Literal):

	def getType(self):
		return STR

	def setAnnotations(self, annotations):
		return self.factory.makeStr(self.value, annotations)

	def accept(self, visitor):
		return visitor.visitStr(self)


class Atom(Term):
	
	def getName(self):
		raise NotImplementedError

	def __str__(self):
		return self.getName()


class Symbol(Atom):
	
	def __init__(self, factory, name, annotations = None):
		Atom.__init__(self, factory, annotations)
		self.name = name
	
	def getName(self):
		return self.name
	
	def isEquivalent(self, other):
		return self.getType() == other.getType() and self.name == other.name

	def isEqual(self, other):
		return self.getType() == other.getType() and self.name == other.name


class Constructor(Symbol):

	def getType(self):
		return CONS

	def isConstant(self):
		return True
	
	def _match(self, other, vars):
		return self.isEquivalent(other)

	def _make(self, vars):
		return self

	def accept(self, visitor):
		return visitor.visitCons(self)


class Variable(Symbol):
	
	def getType(self):
		return VAR
	
	def isConstant(self):
		return False
	
	def _match(self, other, vars):
		name = self.getName()
		if name in vars:
			return vars[name].isEquivalent(other)
		else:
			vars[name] = other
			return True

	def _make(self, vars):
		name = self.getName()
		if name in vars:
			return vars[name]
		else:
			raise ValueError, 'undefined term variable %s' % name

	def accept(self, visitor):
		return visitor.visitVar(self)


class Wildcard(Atom):

	def getType(self):
		return WILDCARD
	
	def getName(self):
		return '_'
	
	def isConstant(self):
		return False
	
	def isEquivalent(self, other):
		return other.type == WILDCARD
	
	def isEqual(self, other):
		return other.type == WILDCARD and self.annotations.isEquivalent(other.annotations)
	
	def _match(self, other, vars):
		return True

	def _make(self, vars):
		raise ValueError, 'Cannot make a term from a wildcard.'

	def accept(self, visitor):
		return visitor.visitWildcard(self)


class List(Term):

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

	def __getitem__(self, index):
		if self.isEmpty():
			raise IndexError
		elif index == 0:
			return self.getHead()
		else:
			return self.getTail().__getitem__(index - 1)

	def insert(self, element):
		return self.factory.makeConsList(element, self)
	
	def accept(self, visitor):
		return visitor.visitList(self)


class _NilList(List):
	
	def __init__(self, factory, annotations = None):
		Term.__init__(self, factory, annotations)

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		return None
	
	def getTail(self):
		return None

	def isConstant(self):
		return True
	
	def isEquivalent(self, other):
		return other is self or (other.type == LIST and other.isEmpty())

	def isEqual(self, other):
		return self.isEquivalent(other) and self.annotations.isEquivalent(other)

	def _match(self, other, vars):
		if self is other:
			return True
		
		if other.type == LIST:
			if other.isEmpty():
				return True
		
		return List._match(self, other, vars)

	def setAnnotations(self, annotations):
		return self.factory.makeNilList(annotations)


class _ConsList(List):

	def __init__(self, factory, head, tail = None, annotations = None):
		Term.__init__(self, factory, annotations)

		self.head = head
		if tail is None:
			self.tail = self.factory.makeNilList()
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

	def isConstant(self):
		return self.head.isConstant() and self.tail.isConstant()
	
	def isEquivalent(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEquivalent(self.head) and other.tail.isEquivalent(self.tail))
		
	def isEqual(self, other):
		return other is self or (other.type == LIST and not other.isEmpty() and other.head.isEqual(self.head) and other.tail.isEqual(self.tail)) and self.annotations.isEquivalent(other.annotations)
	
	def _match(self, other, vars):
		if self is other:
			return True
		
		if other.type == LIST:
			if not other.isEmpty():
				if self.head._match(other.head, vars):
					return self.tail._match(other.tail, vars)
		
		return List._match(self, other, vars)

	def _make(self, vars):
		return self.factory.makeConsList(self.head._make(vars), self.tail._make(vars), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeConsList(self.head, self.tail, annotations)


class Application(Term):

	def __init__(self, factory, name, args = None, annotations = None):
		Term.__init__(self, factory, annotations)

		self.name = name
		if args is None:
			self.args = self.factory.makeNilList()
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
	
	def isConstant(self):
		return self.name.isConstant() and self.args.isConstant()
	
	def isEquivalent(self, other):
		return other is self or (other.type == APPL and other.name == self.name and other.args.isEquivalent(self.args))

	def isEqual(self, other):
		return other is self or (other.type == APPL and other.name == self.name and other.args.isEqual(self.args) and other.annotations.isEquivalent(self.annotations))
		
	def _match(self, other, vars):
		if other is self:
			return True
		
		if other.type == APPL:
			return self.name._match(other.name, vars) and self.args._match(other.args, vars)
		
		return Term._match(self, other, vars)
	
	def _make(self, vars):
		return self.factory.makeAppl(self.name._make(vars), self.args._make(vars), self.annotations)
	
	def setAnnotations(self, annotations):
		return self.factory.makeAppl(self.name, self.args, annotations)

	def accept(self, visitor):
		return visitor.visitAppl(self)


class Visitor:
	
	def visit(self, term):
		assert isinstance(term, Term)
		return term.accept(self)

	def visitTerm(self, term):
		pass

	def visitLit(self,term):
		return self.visitTerm(self, term)
		
	def visitInt(self, term):
		return self.visitLit(self, term)

	def visitReal(self, term):
		return self.visitLit(self, term)

	def visitStr(self, term):
		return self.visitLit(self, term)

	def visitAtom(self,term):
		return self.visitTerm(self, term)
		
	def visitSym(self, term):
		return self.visitAtom(self, term)

	def visitCons(self, term):
		return self.visitSym(term)
	
	def visitVar(self, term):
		return self.visitSym(term)
	
	def visitWildcard(self, term):
		return self.visitAtom(self, term)

	def visitList(self, term):
		return self.visitTerm(self, term)

	def visitAppl(self, term):
		return self.visitTerm(self, term)


class TextWriter(Visitor):
	
	def __init__(self, fp):
		self.fp = fp
	
	def writeTerms(self, terms):
		if terms.getType() == LIST and not terms.isEmpty():
			self.visit(terms.head)
			terms = terms.tail
			while terms.getType() == LIST and not terms.isEmpty():
				self.fp.write(',')
				self.visit(terms.head)
				terms = terms.tail
		if terms.getType() != LIST:
			self.fp.write(',*')
			if terms.getType() != WILDCARD:
				self.visit(terms)

	def writeAnnotations(self, term):
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			self.fp.write('{')
			self.writeTerms(annotations)
			self.fp.write('}')

	def visitInt(self, term):
		self.fp.write(str(term.getValue()))
		self.writeAnnotations(term)
	
	def visitReal(self, term):
		self.fp.write('%g' % term.getValue())
		self.writeAnnotations(term)
	
	def visitStr(self, term):
		s = str(term.getValue())
		s = s.replace('\"', '\\"')
		s = s.replace('\t', '\\t')
		s = s.replace('\r', '\\r')
		s = s.replace('\n', '\\n')
		self.fp.write('"' + s + '"')
		self.writeAnnotations(term)
	
	def visitSym(self, term):
		self.fp.write(str(term.getName()))
		self.writeAnnotations(term)
		
	def visitWildcard(self, term):
		self.fp.write('_')
	
	def visitList(self, term):
		self.fp.write('[')
		self.writeTerms(term)			
		self.fp.write(']')
		self.writeAnnotations(term)

	def visitAppl(self, term):
		self.visit(term.getName())
		self.fp.write('(')
		self.writeTerms(term.getArgs())
		self.fp.write(')')
		self.writeAnnotations(term)
	
