'''Term projection.'''


from aterm.factory import factory
from aterm import visitor


class Subterms(visitor.Visitor):
	'''Project the direct subterms of a term.'''
	
	def visitLit(self, term):
		return factory.makeNil()
	
	def visitList(self, term):
		return term
	
	def visitAppl(self, term):
		return factory.makeList(term.args)

subterms = Subterms().visit


class Subterm(visitor.Visitor):
	'''Project a direct subterm of a term.'''

	def visitTerm(self, term, index):
		raise IndexError('index out of bounds')	

	def visitCons(self, term, index):
		if index == 0:
			return term.head
		else:
			return self.visit(term.tail, index - 1)

	def visitAppl(self, term, index):
		return term.args[index]

subterm = Subterm().visit