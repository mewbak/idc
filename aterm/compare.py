'''Term comparison.'''


from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):
	'''Base class for term comparators.'''
	
	def visitLit(self, term, other):
		return \
			term.type == other.type and \
			term.value == other.value

	def visitNil(self, term, other):
		return \
			types.NIL == other.type

	def visitCons(self, term, other):
		return \
			types.CONS == other.type and \
			self.visit(term.head, other.head) and \
			self.visit(term.tail, other.tail)

	def visitAppl(self, term, other):
		if types.APPL != other.type:
			return False
		if term.name != other.name:
			return False
		if len(term.args) != len(other.args):
			return False
		for term_arg, other_arg in zip(term.args, other.args):
			if not self.visit(term_arg, other_arg):
				return False
		return True
	

class Equivalent(Comparator):
	'''Comparator for determining term equivalence (which does not 
	contemplate annotations).
	'''

	def visit(self, term, other):
		return (
			term is other or
			Comparator.visit(self, term, other)
		)

isEquivalent = Equivalent().visit


class Equal(Equivalent):
	'''Comparator for determining term equality (which contemplates 
	annotations).
	'''

	def compareAnnos(self, terms, others):
		if terms is None:
			return others is None
		else:
			return others is not None and \
				isEquivalent(terms, others)
		
	def visit(self, term, other):
		return \
			Equivalent.visit(self, term, other) and \
			self.compareAnnos(term.annotations, other.annotations)

isEqual = Equal().visit
