'''Facilities for building terms.'''


from aterm import exceptions
from aterm import terms


class _Singleton(type):
	'''Metaclass for the Singleton design pattern. Based on 
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/102187
	'''
	
	def __init__(mcs, name, bases, dic):
		super(_Singleton, mcs).__init__(name, bases, dic)
		mcs.__instance = None
		
	def __call__(mcs, *args, **kargs):
		if mcs.__instance is None:
			mcs.__instance = super(_Singleton, mcs).__call__(*args, **kargs)
		return mcs.__instance


class Factory(object):
	'''An Factory is responsible for make new Terms, either by parsing 
	from string or stream, or via one the of the "make" methods.'''

	__metaclass__ = _Singleton
	
	# TODO: implement maximal sharing

	MAX_PARSE_CACHE_LEN = 512
	
	def __init__(self):
		self.parseCache = {}
		self.__nil = terms.Nil(self)

	def makeInt(self, value, annotations = None):
		'''Creates a new integer literal term'''
		return terms.Integer(self, value, annotations)
	
	def makeReal(self, value, annotations = None):
		'''Creates a new real literal term'''
		return terms.Real(self, value, annotations)

	def makeStr(self, value, annotations = None):
		'''Creates a new string literal term'''
		return terms.String(self, value, annotations)

	def makeNil(self, annotations = None):
		'''Creates a new empty list term'''
		if annotations:
			return terms.Nil(self, annotations)
		else:
			return self.__nil

	def makeCons(self, head, tail = None, annotations = None):
		'''Creates a new extended list term'''
		return terms.Cons(self, head, tail, annotations)

	def makeList(self, seq, annotations = None):
		'''Creates a new list from a sequence.'''
		accum = self.makeNil()
		for i in xrange(len(seq) - 1, -1, -1):
			accum = self.makeCons(seq[i], accum)
		if annotations is not None:
			accum = accum.setAnnotations(annotations)
		return accum
	
	# TODO: add a makeTuple method
	
	def makeAppl(self, name, args = None, annotations = None):
		'''Creates a new appplication term'''
		return terms.Application(self, name, args, annotations)

	def makeWildcard(self, annotations = None):
		'''Creates a new wildcard term'''
		return terms.Wildcard(self, annotations)

	def makeVar(self, name, pattern, annotations = None):
		'''Creates a new variable term'''
		return terms.Variable(self, name, pattern, annotations)

	def coerce(self, value, name = None):
		'''Coerce an object to a term. Value must be an int, a float, a string, 
		a sequence of terms, or a term.'''
		
		if isinstance(value, terms.Term):
			return value
		elif isinstance(value, int):
			return self.makeInt(value)
		elif isinstance(value, float):
			return self.makeReal(value)
		elif isinstance(value, basestring):
			return self.makeStr(value)
		elif isinstance(value, list):
			return self.makeList(value)
		elif isinstance(value, tuple):
			return self.makeList(value)
		else:
			msg = "argument"
			if not name is None:
				msg += " " + name
			msg += " is neither a term, a literal, or a list: "
			msg += repr(value)
			raise TypeError(msg)

	def _parse(self, lexer):
		'''Creates a new term by parsing a string.'''
		
		from aterm.lexer import Lexer
		from aterm.parser import Parser
		from antlr import ANTLRException

		parser = Parser(lexer, factory = self)
		try:
			return parser.aterm()
		except ANTLRException, ex:
			raise exceptions.ParseException(str(ex))
	
	def readFromTextFile(self, fp):
		'''Creates a new term by parsing from a text stream.'''

		from aterm.lexer import Lexer
		lexer = Lexer(fp = fp)
		return self._parse(lexer)

	def parse(self, buf):
		'''Creates a new term by parsing a string.'''
		
		try:
			return self.parseCache[buf]
		except KeyError:
			pass
		
		from aterm.lexer import Lexer
		lexer = Lexer(buf)
		result = self._parse(lexer)
		
		if len(self.parseCache) > self.MAX_PARSE_CACHE_LEN:
			# TODO: use a LRU cache policy
			self.parseCache.clear()
		self.parseCache[buf] = result
			
		return result

	def match(self, pattern, other):
		'''Matches the term to a string pattern and a list of arguments. 
		First the string pattern is parsed into an Term. .'''
		
		return self.parse(pattern).match(other)

	def make(self, pattern, *args, **kargs):
		'''Creates a new term from a string pattern and a list of arguments. 
		First the string pattern is parsed into an Term. Then the holes in 
		the pattern are filled with arguments taken from the supplied list of 
		arguments.'''
		
		_pattern = self.parse(pattern)
		i = 0
		_args = []
		for i in range(len(args)):
			_args.append(self.coerce(args[i], str(i)))
			i += 1
		
		_kargs = {}
		for name, value in kargs.iteritems():
			_kargs[name] = self.coerce(value, "'" + name + "'")

		return _pattern.make(*_args, **_kargs)


