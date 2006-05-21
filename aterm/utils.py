'''Several utility classes.'''


from aterm import visitor


class Constness(visitor.Visitor):
	'''Visitor for determining if a term is constant.'''
	
	def visitLit(self, term):
		return True

	def visitNil(self, term):
		return True

	def visitCons(self, term):
		return \
			self.visit(term.getHead()) and \
			self.visit(term.getTail())

	def visitAppl(self, term):
		return \
			self.visit(term.getName()) and \
			self.visit(term.getArgs())		

	def visitPlaceholder(self, term):
		return False


isConstant = Constness()


class Hash(visitor.Visitor):
	'''Base class for term comparators.'''
	
	# TODO: use a more efficient hash function
	
	def visit(self, term):
		value = visitor.Visitor.visit(self, term)
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			return hash((value, self.visit(annotations)))
		else:
			return value

	def visitLit(self, term):
		return hash(term.getValue())

	def visitNil(self, term):
		return hash(())

	def visitCons(self, term):
		return hash((
			self.visit(term.getHead()),
			self.visit(term.getTail()),
		))

	def visitAppl(self, term):
		return hash((
			self.visit(term.getName()),
			self.visit(term.getArgs()),
		))

	def visitWildcard(self, term):
		return hash(None)

	def visitVar(self, term):
		return hash((
			term.getName(),
			self.visit(term.getPattern()),
		))


