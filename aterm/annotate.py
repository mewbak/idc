'''Term annotation.'''


from aterm import visitor


class Annotator(visitor.Visitor):
	
	def visit(self, term, annotations):
		if term.annotations is annotations:
			return term
		else:
			return visitor.Visitor.visit(self, term, annotations)
		
	def visitInt(self, term, annotations):
		return term.factory.makeInt(term.value, annotations)

	def visitReal(self, term, annotations):
		return term.factory.makeReal(term.value, annotations)
		
	def visitStr(self, term, annotations):
		return term.factory.makeStr(term.value, annotations)
	
	def visitNil(self, term, annotations):
		return term.factory.makeNil(annotations)

	def visitCons(self, term, annotations):
		return term.factory.makeCons(term.head, term.tail, annotations)

	def visitAppl(self, term, annotations):
		return term.factory.makeAppl(term.name, term.args, annotations)

annotate = Annotator().visit


class Remover(visitor.Visitor):
	
	def __init__(self, pattern):
		visitor.Visitor.__init__(self)
		self.pattern = pattern
		
	def visitNil(self, term):
		return term
	
	def visitCons(self, term):
		tail = self.visit(term.tail)
		if term.factory.match(self.pattern, term.head):
			return tail
		elif tail is term.tail:
			return term
		else:
			return term.factory.makeCons(term.head, tail, term.annotations)

