'''List operations.'''


from aterm.factory import factory
from aterm import visitor


class Operation(visitor.Visitor):
	'''Base visitor class for list operations.'''
	
	def visitTerm(self, term, *args, **kargs):
		return TypeError('not a list term', term)
		

class Empty(Operation):
	
	def visitNil(self, term):
		return True
	
	def visitCons(self, term):
		return False

empty = Empty().visit


class Length(Operation):
	
	def visitNil(self, term):
		return 0
	
	def visitCons(self, term, other):
		return self.visit(term.tail) + 1
		
length = Length().visit


class Extend(Operation):
	
	def visitNil(self, term, other):
		return other
	
	def visitCons(self, term, other):
		return factory.makeCons(
			term.head, 
			self.visit(term.tail, other),
			term.annotations
		)

extend = Extend().visit


def append(term, other):
	return extend(term, factory.makeCons(other, factory.makeNil()))


class Insert(Operation):
	
	def visitNil(self, term, index, other):
		if index == 0:
			return factory.makeCons(other, term)
		else:
			raise IndexError('index out of bound')
	
	def visitCons(self, term, other):
		if index == 0:
			return factory.makeCons(other, term)
		else:
			return factory.makeCons(
				term.head,
				self.visit(term.tail, index - 1, other),
				term.annotations,
			)

insert = Insert().visit


class Reverse(Operation):
	
	def __call__(self, term):
		return self.visit(term, factory.makeNil())
		
	def visitNil(self, term, accum):
		return accum
		
	def visitCons(self, term, accum):
		return self.visit(
			term.tail,
			factory.makeCons(term.head, accum),
		)
		
reverse = Reverse()