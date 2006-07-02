'''Term annotation.'''


from aterm import visitor


class Annotator(visitor.Visitor):
	'''Annotate a term.'''
	
	def visit(self, term, annos):
		if term.annotations is annos:
			return term
		else:
			return visitor.Visitor.visit(self, term, annos)
			
	def visitInt(self, term, annos):
		return term.factory.makeInt(term.value, annos)

	def visitReal(self, term, annos):
		return term.factory.makeReal(term.value, annos)
		
	def visitStr(self, term, annos):
		return term.factory.makeStr(term.value, annos)
	
	def visitNil(self, term, annos):
		return term.factory.makeNil(annos)

	def visitCons(self, term, annos):
		return term.factory.makeCons(term.head, term.tail, annos)

	def visitAppl(self, term, annos):
		return term.factory.makeAppl(term.name, term.args, annos)

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

