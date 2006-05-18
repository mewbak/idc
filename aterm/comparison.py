from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):

	def __init__(self):
		pass
	
	def compare(self, term, other):
		if term is other:
			return True
		
		if term.getType() != other.getType():
			return False
		
		return term.accept(self, other)

	def visitLit(self, term, other):
		return term.getType() == other.getType() and term.getValue() == other.getValue()
		
	def visitWildcard(self, term, other):
		return types.WILDCARD == other.getType()

	def visitVar(self, term, other):
		return other.getType() == types.VAR and \
			term.getName() == other.getName() and \
			self.compare(term.getPattern(), other.getPattern())
	
	def visitNilList(self, term, other):
		return other.getType() == types.LIST and \
			other.isEmpty()

	def visitConsList(self, term, other):
		return other.getType() == types.LIST and \
			not other.isEmpty() and \
			self.compare(term.getHead(), other.getHead()) and \
			self.compare(term.getTail(), other.getTail())

	def visitAppl(self, term, other):
		return other.getType() == types.APPL and \
			self.compare(term.getName(), other.getName()) and \
			self.compare(term.getArgs(), other.getArgs())


class EqualityComparator(Comparator):
	
	def compare(self, term, other):
		if term is other:
			return True
		
		if term.getType() != other.getType():
			return False
		
		return term.accept(self, other) and Comparator().compare(term.getAnnotations(), other.getAnnotations())


class MatchingComparator(Comparator):

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
		
	def compare(self, term, other):
		return term.accept(self, other)
	
	def visitWildcard(self, term, other):
		self.args.append(other)
		return True

	def visitVar(self, term, other):
		name = term.getName()
		try:
			value = self.kargs[name]
			if not self.kargs[name].isEquivalent(other):
				return False
			return True
		except KeyError:
			if not MatchingComparator([], self.kargs).compare(term.getPattern(), other):
				return False
			self.kargs[name] = other
			return True
	

	
	