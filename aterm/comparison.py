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
		return term.getType() == other.getType()

	def visitVar(self, term, other):
		return term.getName() == other.getName() and \
			self.compare(term.getPattern(), other.getPattern())
	
	def visitNilList(self, term, other):
		return other.isEmpty()

	def visitConsList(self, term, other):
		return not other.isEmpty() and \
			self.compare(term.getHead(), other.getHead()) and \
			self.compare(term.getTail(), other.getTail())

	def visitAppl(self, term, other):
		return \
			self.compare(term.getName(), other.getName()) and \
			self.compare(term.getArgs(), other.getArgs())


class EqualityComparator(Comparator):
	
	def compare(self, term, other):
		if term is other:
			return True
		
		if term.getType() != other.getType():
			return False
		
		return term.accept(self, other) and Comparator().compare(term.getAnnotations(), other.getAnnotations())

