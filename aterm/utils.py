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


class Hash(visitor.Visitor):
	'''Base class for term comparators.'''
	
	# TODO: use a more efficient hash function
	
	def hash(self, term):
		'''Compares two terms.'''
		value = self.visit(term)
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
			self.hash(term.getHead()),
			self.hash(term.getTail()),
		))

	def visitAppl(self, term):
		return hash((
			self.hash(term.getName()),
			self.hash(term.getArgs()),
		))

	def visitWildcard(self, term):
		return hash(None)

	def visitVar(self, term):
		return hash((
			term.getName(),
			self.hash(term.getPattern()),
		))


