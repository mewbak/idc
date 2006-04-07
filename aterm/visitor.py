'''Term visiting.'''


class Visitor:
	'''Base class for term visitors.'''
	
	def __init__(self):
		pass
	
	def visit(self, term, *args, **kargs):
		return term.accept(self, *args, **kargs)

	def visitTerm(self, term, *args, **kargs):
		pass

	def visitLit(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)
		
	def visitInt(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitReal(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitStr(self, term, *args, **kargs):
		return self.visitLit(self, term, *args, **kargs)

	def visitWildcard(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)

	def visitVar(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
	
	def visitList(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)

	def visitNilList(self, term, *args, **kargs):
		return self.visitList(self, term, *args, **kargs)

	def visitConsList(self, term, *args, **kargs):
		return self.visitList(self, term, *args, **kargs)

	def visitAppl(self, term, *args, **kargs):
		return self.visitTerm(self, term, *args, **kargs)


