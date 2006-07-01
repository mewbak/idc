'''Term projection.'''


from aterm.factory import factory
from aterm import visitor


class Subterms(visitor.Visitor):
	
	def visitLit(self, term):
		return factory.makeNil()
	
	def visitList(self, term):
		return term
	
	def visitAppl(self, term):
		return factory.makeList(term.args)

subterms = Subterms().visit