'''Visitors for term comparisons.'''


from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):
	'''Base class for term comparators.'''
	
	def compare(self, term, other):
		'''Compares two terms.'''
		return self.visit(term, other)

	def visitLit(self, term, other):
		return \
			term.getType() == other.getType() and \
			term.getValue() == other.getValue()
		
	def visitWildcard(self, term, other):
		return \
			types.WILDCARD == other.getType()

	def visitVar(self, term, other):
		return \
			types.VAR == other.getType() and \
			term.getName() == other.getName() and \
			self.compare(term.getPattern(), other.getPattern())
	
	def visitNil(self, term, other):
		return \
			types.LIST == other.getType() and \
			other.isEmpty()

	def visitCons(self, term, other):
		return \
			types.LIST == other.getType() and \
			not other.isEmpty() and \
			self.compare(term.getHead(), other.getHead()) and \
			self.compare(term.getTail(), other.getTail())

	def visitAppl(self, term, other):
		return \
			types.APPL == other.getType() and \
			self.compare(term.getName(), other.getName()) and \
			self.compare(term.getArgs(), other.getArgs())		
	

class Equivalence(Comparator):
	'''Comparator for determining term equivalence (which does not 
	contemplate annotations).
	'''

	def compare(self, term, other):
		return \
			term is other or \
			Comparator.compare(self, term, other)


equivalence = Equivalence()


class Equality(Equivalence):
	'''Comparator for determining term equality (which contemplates 
	annotations).
	'''

	def compare(self, term, other):
		return \
			Equivalence.compare(self, term, other) and \
			equivalence.compare(term.getAnnotations(), other.getAnnotations())


equality = Equality()


class Matcher(Comparator):
	'''Comparator for performing pattern matching.'''

	def __init__(self, args = None, kargs = None):
		Comparator.__init__(self)
		
		if args is None:
			self.args = []
		else:
			self.args = args		
		
		if kargs is None:
			self.kargs = {}
		else:
			self.kargs = kargs
	
	def visitLit(self, term, other):
		return \
			term is other or \
			Comparator.visitLit(self, term, other)
	
	def visitWildcard(self, term, other):
		self.args.append(other)
		return True

	def visitVar(self, term, other):
		name = term.getName()
		try:
			value = self.kargs[name]
		except KeyError:
			if not Matcher([], self.kargs).compare(term.getPattern(), other):
				return False
			else:
				self.kargs[name] = other
				return True
		else:
			return equivalence.compare(value, other)

	
