'''Several utility classes.'''


from aterm import visitor


class Constness(visitor.Visitor):
	'''Visitor for determining if a term is constant.'''
	
	def isConstant(self, term):
		return self.visit(term)

	def visitLit(self, term):
		return True

	def visitNil(self, term):
		return True

	def visitCons(self, term):
		return \
			self.isConstant(term.getHead()) and \
			self.isConstant(term.getTail())

	def visitAppl(self, term):
		return \
			self.isConstant(term.getName()) and \
			self.isConstant(term.getArgs())		

	def visitPlaceholder(self, term):
		return False


constness = Constness()
