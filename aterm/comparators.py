'''Visitors for term comparisons.'''


from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):
	'''Base class for term comparators.'''
	
	def visitLit(self, term, other):
		return \
			term.getType() == other.getType() and \
			term.getValue() == other.getValue()

	def visitNil(self, term, other):
		return \
			types.LIST == other.getType() and \
			other.isEmpty()

	def visitCons(self, term, other):
		return \
			types.LIST == other.getType() and \
			not other.isEmpty() and \
			self.visit(term.getHead(), other.getHead()) and \
			self.visit(term.getTail(), other.getTail())

	def visitAppl(self, term, other):
		return \
			types.APPL == other.getType() and \
			self.visit(term.getName(), other.getName()) and \
			self.visit(term.getArgs(), other.getArgs())		

	def visitWildcard(self, term, other):
		return \
			types.WILDCARD == other.getType()

	def visitVar(self, term, other):
		return \
			types.VAR == other.getType() and \
			term.getName() == other.getName() and \
			self.visit(term.getPattern(), other.getPattern())
	

class Equivalence(Comparator):
	'''Comparator for determining term equivalence (which does not 
	contemplate annotations).
	'''

	def visit(self, term, other):
		return \
			term is other or \
			Comparator.visit(self, term, other)


isEquivalent = Equivalence()


class Equality(Equivalence):
	'''Comparator for determining term equality (which contemplates 
	annotations).
	'''

	def visit(self, term, other):
		return \
			Equivalence.visit(self, term, other) and \
			isEquivalent(term.getAnnotations(), other.getAnnotations())


isEqual = Equality()


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
			if not Matcher([], self.kargs)(term.getPattern(), other):
				return False
			else:
				self.kargs[name] = other
				return True
		else:
			return isEquivalent(value, other)

	
