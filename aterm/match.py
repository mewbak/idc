'''Term pattern matching.'''


from aterm import visitor
from aterm import parser


class Match(object):
	'''Match object.'''
	
	def __init__(self):
		self.args = []
		self.kargs = {}
	
	def __iter__(self):
		return iter(self.args)


class Matcher(visitor.Visitor):

	def match(self, term):
		match = Match()
		if self.visit(term, match):
			return match
		else:
			return None
	

class Int(Matcher):
	
	def __init__(self, value):
		Matcher.__init__(self)
		assert isinstance(value, int)
		self.value = value

	def visitTerm(self, term, match):
		return False

	def visitInt(self, term, match):
		return self.value == term.value


class Real(Matcher):
	
	def __init__(self, value):
		Matcher.__init__(self)
		assert isinstance(value, float)
		self.value = value

	def visitTerm(self, term, match):
		return False

	def visitReal(self, term, match):
		return self.value == term.value


class Str(Matcher):
	
	def __init__(self, value):
		Matcher.__init__(self)
		assert isinstance(value, basestring)
		self.value = value

	def visitTerm(self, term, match):
		return False

	def visitStr(self, term, match):
		return self.value == term.value


class Nil(Matcher):
	
	def visitTerm(self, term, match):
		return False

	def visitNil(self, term, match):
		return True


class Cons(Matcher):
	
	def __init__(self, head, tail):
		Matcher.__init__(self)
		assert isinstance(head, Matcher)
		assert isinstance(tail, Matcher)
		self.head = head
		self.tail = tail
	
	def visitTerm(self, term, match):
		return False

	def visitCons(self, term, match):
		return (
			self.head.visit(term.head, match) and 
			self.tail.visit(term.tail, match)
		)


class Appl(Matcher):
	
	def __init__(self, name, args):
		Matcher.__init__(self)
		assert isinstance(name, basestring)
		self.name = name
		self.args = tuple(args)
	
	def visitTerm(self, term, match):
		return False

	def visitAppl(self, term, match):
		if self.name != term.name:
			return False
		if len(self.args) != len(term.args):
			return False
		for arg, term_arg in zip(self.args, term.args):
			if not arg.visit(term_arg, match):
				return False
		return True


class ApplCons(Matcher):
	
	def __init__(self, name, args):
		Matcher.__init__(self)
		assert isinstance(name, Matcher)
		assert isinstance(args, Matcher)
		self.name = name
		self.args = args
	
	def visitTerm(self, term, match):
		return False

	def visitAppl(self, term, match):
		factory = term.factory
		return (
			self.name.visit(factory.makeStr(term.name), match) and 
			self.args.visit(factory.makeList(term.args), match)
		)


class Wildcard(Matcher):
	
	def visitTerm(self, term, match):
		match.args.append(term)
		return True


class Var(Matcher):
	
	def __init__(self, name):
		Matcher.__init__(self)
		assert isinstance(name, basestring)
		self.name = name
	
	def visitTerm(self, term, match):
		try:
			value = match.kargs[self.name]
		except KeyError:
			match.kargs[self.name] = term
			return True
		else:
			return value == term


class Seq(Matcher):
	
	def __init__(self, pre, post):
		Matcher.__init__(self)
		assert isinstance(pre, Matcher)
		assert isinstance(post, Matcher)
		self.pre = pre
		self.post = post

	def visitTerm(self, term, match):
		temp = Match()
		temp.kargs = match.kargs
		return (
			self.pre.visit(term, temp) and 
			self.post.visit(term, match)
		)


class Parser(parser.Parser):
	
	def handleInt(self, value):
		return Int(value)

	def handleReal(self, value):
		return Real(value)

	def handleStr(self, value):
		return Str(value)

	def handleNil(self):
		return Nil()

	def handleCons(self, head, tail):
		return Cons(head, tail)
	
	def handleAppl(self, name, args):
		return Appl(name, args)
	
	def handleAnnos(self, term, annos):
		# ignore annotations
		return term
	
	def handleWildcard(self):
		return Wildcard()
	
	def handleVar(self, name):
		return Var(name)

	def handleSeq(self, pre, post):
		return Seq(pre, post)
		
	def handleApplCons(self, name, args):
		return ApplCons(name, args)
	