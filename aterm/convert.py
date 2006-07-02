'''Term conversion.'''


from aterm import visitor


class ToInt(visitor.Visitor):
	'''Convert an integer term to its integer value.'''
	
	def visitTerm(self, term):
		raise TypeError('not an integer term', term)
	
	def visitInt(self, term):
		return term.value

toInt = ToInt().visit


class ToReal(visitor.Visitor):
	'''Convert a real term to its real value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a real term', term)
	
	def visitReal(self, term):
		return term.value

toReal = ToReal().visit


class ToStr(visitor.Visitor):
	'''Convert a string term to its string value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a string term', term)
	
	def visitStr(self, term):
		return term.value

toStr = ToStr().visit


class ToLit(visitor.Visitor):
	'''Convert a literal term to its value.'''
	
	def visitTerm(self, term):
		raise TypeError('not a literal term', term)
	
	def visitLit(self, term):
		return term.value

toLit = ToLit().visit


class ToList(visitor.Visitor):
	'''Convert a list term to a list of terms.'''

	def visitTerm(self, term):
		raise TypeError('not a list term', term)
	
	def visitNil(self, term):
		return []

	def visitCons(self, term):
		head = term.head
		tail = self.visit(term.tail)
		return [head] + tail

toList = ToList().visit


class ToObj(visitor.Visitor):
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
	
toObj = ToObj().visit
