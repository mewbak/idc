'''Term visiting.'''


class Visitor:
	'''Base class for term visitors.'''
	
	def __init__(self):
		pass
	
	def visit(self, term, *args, **kargs):
		'''Visit the given term.'''
		return term.accept(self, *args, **kargs)

	def visitTerm(self, term, *args, **kargs):
		raise NotImplementedError

	def visitLit(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
		
	def visitInt(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitReal(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitStr(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)
	
	def visitList(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitNil(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitCons(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitAppl(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitPlaceholder(self,term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
		
	def visitWildcard(self, term, *args, **kargs):
		return self.visitPlaceholder(term, *args, **kargs)

	def visitVar(self, term, *args, **kargs):
		return self.visitPlaceholder(term, *args, **kargs)

