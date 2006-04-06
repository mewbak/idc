'''Module for term representation and manipulation. Loosely inspired on the Java
version of the ATerm library.'''

# TODO: maximal sharing
# TODO: annotations

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import antlr
from aterm.lexer import Lexer
from aterm.parser import Parser


# Term types
INT = 1
REAL = 2
STR = 3
LIST = 4
CONS = 5
APPL = 6
WILDCARD = 7
VAR = 8


class BaseException(Exception):
	"""Base class for all term-related exceptions."""
	pass


class ParseException(BaseException):
	"""Error parsing terms."""
	pass

	
class PatternMismatchException(BaseException):
	"""Term does not match pattern."""	
	pass


class EmptyListException(BaseException):
	"""Attempt to access beyond the end of the list."""
	pass


class PlaceholderException(BaseException):
	"""Operation invalid for an unbound placeholder term."""
	pass


class Factory:
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

	def makeVar(self, name, pattern, annotations = None):
		'''Creates a new variable term'''
		return Variable(self, name, pattern, annotations)

	def makeWildcard(self, annotations = None):
		'''Creates a new wildcard term'''
		return Wildcard(self, annotations)

	def makeNilList(self, annotations = None):
		'''Creates a new empty list term'''
		return NilList(self, annotations)

	def makeConsList(self, head, tail = None, annotations = None):
		'''Creates a new extended list term'''
		return ConsList(self, head, tail, annotations)

	def makeList(self, seq, annotations = None):
		res = self.makeNilList()
		for i in range(len(seq) - 1, -1, -1):
			res = self.makeConsList(seq[i], res)
		if annotations is not None:
			res = res.setAnnotations(annotations)
		return res
	
	# TODO: add a makeTuple method?
	
	def makeAppl(self, name, args = None, annotations = None):
		'''Creates a new appplication term'''
		return Application(self, name, args, annotations)

	def readFromTextFile(self, fp):
		'''Creates a new term by parsing from a text stream.'''
		
		try:
			lexer = Lexer(fp)
			parser = Parser(lexer, factory = self)
			return parser.term()
		except antlr.ANTLRException, ex:
			# FIXME: this is not working
			raise ParseException(str(ex))
	
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

	def match(self, pattern, other, args = None, kargs = None):
		'''Matches the term to a string pattern and a list of arguments. 
		First the string pattern is parsed into an Term. .'''
		
		_pattern = self.parse(pattern)
		
		try:
			_pattern._match(other, args, kargs)
		except PatternMismatchException:
			return False
		
		return True

	def make(self, pattern, *args, **kargs):
		'''Creates a new term from a string pattern and a list of arguments. 
		First the string pattern is parsed into an Term. Then the holes in 
		the pattern are filled with arguments taken from the supplied list of 
		arguments.'''
		
		_pattern = self.parse(pattern)
		i = 0
		_args = []
		for i in range(len(args)):
			_args.append(self._castArg(str(i), args[i]))
			i += 1
		
		_kargs = {}
		for name, value in kargs.iteritems():
			_kargs[name] = self._castArg("'" + name + "'", value)

		return _pattern._make(_args, _kargs)
		
	def _castArg(self, name, value):
		if isinstance(value, Term):
			return value
		elif isinstance(value, Term):
			return self.makeInt(value)
		elif isinstance(value, int):
			return self.makeInt(value)
		elif isinstance(value, float):
			return self.makeReal(value)
		elif isinstance(value, basestring):
			return self.makeStr(value)
		elif isinstance(value, list):
			return self.makeList(value)
		else:
			raise TypeError, "argument %s is neither a term, a literal, or a list: %r" % (name, value)	


class Term:
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

	def isConstant(self):
		'''Whether this term is constants, as opposed to have variables or wildcards.'''
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
		except PatternMismatchException:
			return False
		
		return True
	
	def _match(self, other, args, kargs):
		raise PatternMismatchException

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
		'''Returns the annotation list.'''
		
		if self.__annotations is None:
			return self.factory.makeNilList()
		else:
			return self.__annotations

	def __getattr__(self, name):
		'''Provide attributes 'type' and 'annotations', 	shorthand  for 
		getType() and getAnnotations() methods respectively.'''
		
		if name == 'type':
			return self.getType()
		elif name == 'annotations':
			return self.getAnnotations()
		else:
			raise AttributeError, "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
			
	def __setattr__(self, name, value):
		'''Prevent modification of term attributes'''
		
		if name in self.__dict__ or name in ('type', 'annotations'):
			raise TypeError, "attempt to modify read-only term attribute '%s'" % name
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
		self.value = value

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
		
		return Term._match(self, other, args, kargs)

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

	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class String(Literal):

	def getType(self):
		return STR

	def getSymbol(self):
		return self.getValue()

	def setAnnotations(self, annotations):
		return self.factory.makeStr(self.value, annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class Wildcard(Term):

	def getType(self):
		return WILDCARD
	
	def getSymbol(self):
		return '_'
	
	def isConstant(self):
		return False
	
	def _isEquivalent(self, other):
		return other.getType() == WILDCARD
	
	def _isEqual(self, other):
		return self._isEquivalent(other)
	
	def _match(self, other, args, kargs):
		args.append(other)
		return other

	def _make(self, args, kargs):
		try:
			return args.pop(0)
		except IndexError:
			raise TypeError, 'insufficient number of arguments'

	def accept(self, visitor, *args, **kargs):
		return visitor.visitWildcard(self, *args, **kargs)


class Variable(Term):
	
	def __init__(self, factory, name, pattern, annotations = None):
		Term.__init__(self, factory, annotations)
		self.name = name
		self.pattern = pattern
	
	def getType(self):
		return VAR
	
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
				raise PatternMismatchException
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
			raise ValueError, 'undefined term variable %s' % name

	def accept(self, visitor, *args, **kargs):
		return visitor.visitVar(self, *args, **kargs)


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
	
	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class NilList(List):
	
	def __init__(self, factory, annotations = None):
		Term.__init__(self, factory, annotations)

	def isEmpty(self):
		return True
	
	def getLength(self):
		return 0

	def getHead(self):
		raise EmptyListException
	
	def getTail(self):
		raise EmptyListException

	def isConstant(self):
		return True
	
	def _isEquivalent(self, other):
		return other.getType() == LIST and other.isEmpty()

	def _isEqual(self, other):
		return self._isEquivalent(other)

	def _match(self, other, args, kargs):
		if self is other:
			return other
		
		if other.getType() == LIST:
			if other.isEmpty():
				return other
				
		raise PatternMismatchException

	def setAnnotations(self, annotations):
		return self.factory.makeNilList(annotations)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitNilList(self, *args, **kargs)


class ConsList(List):

	def __init__(self, factory, head, tail = None, annotations = None):
		Term.__init__(self, factory, annotations)

		if not isinstance(head, Term):
			raise TypeError, "head is not a term: %r" % head
		self.head = head
		if tail is None:
			self.tail = self.factory.makeNilList()
		else:
			if not isinstance(tail, (List, Variable, Wildcard)):
				raise TypeError, "tail is not a list, variable, or wildcard term: %r" % tail
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
	
	def _isEquivalent(self, other):
		return (
			other.getType() == LIST and not other.isEmpty() and 
			other.head.isEquivalent(self.head) and 
			other.tail.isEquivalent(self.tail)
		)
		
	def _isEqual(self, other):
		return (
			other.getType() == LIST and not other.isEmpty() and 
			other.head.isEqual(self.head) and 
			other.tail.isEqual(self.tail)
		)
	
	def _match(self, other, args, kargs):
		if self is other:
			return other
		
		if other.getType() == LIST:
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

	def __init__(self, factory, name, args = None, annotations = None):
		Term.__init__(self, factory, annotations)

		if not isinstance(name, (String, Variable, Wildcard)):
			raise TypeError, "name is not a string, variable, or wildcard term: %r" % name
		self.name = name
		if args is None:
			self.args = self.factory.makeNilList()
		else:
			if not isinstance(args, (List, Variable, Wildcard)):
				raise TypeError, "args is not a list term: %r" % args
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
	
	def _isEquivalent(self, other):
		return other.getType() == APPL and self.name.isEquivalent(other.name) and self.args.isEquivalent(other.args)

	def _isEqual(self, other):
		return other.getType() == APPL and self.name.isEqual(other.name) and self.args.isEqual(other.args)
		
	def _match(self, other, args, kargs):
		if other.getType() == APPL:
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


class Visitor:
	
	def visit(self, term, *args, **kargs):
		if not isinstance(term, Term):
			raise TypeError, 'not a term: %r' % term
		return term.accept(self, *args, **kargs)

	def visitTerm(self, term, *args, **kargs):
		pass

	def visitLit(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)
		
	def visitInt(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitReal(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitStr(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitWildcard(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)

	def visitVar(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
	
	def visitList(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)

	def visitNilList(self, term, *args, **kargs):
		return self.visitList(self, term, *args, **kargs)

	def visitConsList(self, term, *args, **kargs):
		return self.visitList(self, term, *args, **kargs)

	def visitAppl(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)


class TextWriter(Visitor):
	
	def __init__(self, fp):
		self.fp = fp

	def writeAnnotations(self, term):
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			self.fp.write('{')
			in_list = self.in_list.set(True)
			self.writeTerms(annotations)
			self.in_list.unset(in_list)
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
	
	def visitNilList(self, term, inside_list = False):
		if not inside_list:
			self.fp.write('[]')
			self.writeAnnotations(term)

	def visitConsList(self, term, inside_list = False):
		if not inside_list:
			self.fp.write('[')	 
		head = term.getHead()
		self.visit(head)
		tail = term.getTail()
		last = tail.getType() == LIST and tail.isEmpty()
		if not last:
			self.fp.write(",")
			self.visit(tail, inside_list = True)		
		if not inside_list:
			self.fp.write(']')
			self.writeAnnotations(term)

	def visitAppl(self, term):
		name = term.getName()
		# TODO: verify strings
		self.fp.write(name.getSymbol())
		args = term.getArgs()
		if name.getType() != STR or name.getValue() == '' or not args.isEquivalent(args.factory.makeNilList()):
			self.fp.write('(')
			self.visit(args, inside_list = True)
			self.fp.write(')')
		self.writeAnnotations(term)

	def visitVar(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		self.fp.write(str(term.getName()))
		pattern = term.getPattern()
		if pattern.getType() != WILDCARD:
			self.fp.write('=')
			self.visit(pattern)
		
	def visitWildcard(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		else:
			self.fp.write('_')

