'''Term conversion.'''


from aterm import visitor


class _ToInt(visitor.Visitor):
	'''Convert an integer term to its integer value.'''
	
	def visitTerm(self, term):
		raise TypeError('not an integer term', term)
	
	def visitInt(self, term):
		return term.value

toInt = _ToInt().visit


class _ToReal(visitor.Visitor):
	'''Convert a real term to its real value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a real term', term)
	
	def visitReal(self, term):
		return term.value

toReal = _ToReal().visit


class _ToStr(visitor.Visitor):
	'''Convert a string term to its string value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a string term', term)
	
	def visitStr(self, term):
		return term.value

toStr = _ToStr().visit


class _ToLit(visitor.Visitor):
	'''Convert a literal term to its value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a literal term', term)
	
	def visitLit(self, term):
		return term.value

toLit = _ToLit().visit


class _ToList(visitor.Visitor):
	'''Convert a list term to a list of terms.'''

	def visitTerm(self, term):
		raise TypeError('not a list term', term)
	
	def visitNil(self, term):
		return []

	def visitCons(self, term):
		head = term.head
		tail = self.visit(term.tail)
		return [head] + tail

toList = _ToList().visit


class _ToObj(visitor.Visitor):
	'''Recursively convert literal and list terms to the corresponding
	Python objects.'''
	
	def visitTerm(self, term):
		raise TypeError('term not convertible', term)
	
	def visitLit(self, term):
		return term.value

	def visitNil(self, term):
		return []

	def visitCons(self, term):
		head = self.visit(term.head)
		tail = self.visit(term.tail)
		return [head] + tail
	
toObj = _ToObj().visit
