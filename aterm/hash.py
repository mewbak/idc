'''Term hash computation.'''


from aterm import visitor


class StructuralHash(visitor.Visitor):
	'''Perform hashing without considering.'''
	
	def hash(cls, term):
		return cls().visit(term)
	hash = classmethod(hash)

	# TODO: use a more efficient hash function

	def visitLit(self, term):
		return hash((
			term.type,
			term.value
		))

	def visitNil(self, term):
		return hash((
			term.type,
		))

	def visitCons(self, term):
		return hash((
			term.type,
			self.visit(term.head),
			self.visit(term.tail),
		))

	def visitAppl(self, term):
		return hash((
			term.type,
			term.name,
			term.args,
		))


class Hash(StructuralHash):
	'''Perform hashing.'''
	
	# TODO: use a more efficient hash function
	
	def visit(self, term):
		term_hash = StructuralHash.visit(self, term)
		if term.annotations:
			annos_hash = StructuralHash.hash(term.annotations)
			return hash(term_hash, annos_hash)
		else:
			return term_hash


# TODO: implement a XML writer