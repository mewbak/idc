'''List operations.'''


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
	
	def visitCons(self, term):
		return self.visit(term.tail) + 1
		
length = Length().visit


class Item(Operation):
	
	def visitNil(self, term, index):
		raise IndexError('index out of bounds')
	
	def visitCons(self, term, index):
		if index == 0:
			return term.head
		else:
			return self.visit(term.tail, index - 1)

item = Item().visit


class Iter(Operation):
	'''List term iterator.'''

	def __init__(self, term):
		Operation.__init__(self)
		self.term = term
		
	def next(self):
		return self.visit(self.term)
	
	def visitNil(self, term):
		raise StopIteration
	
	def visitCons(self, term):
		head = term.head
		self.term = term.tail
		return head


class Extend(Operation):
	
	def visitNil(self, term, other):
		return other
	
	def visitCons(self, term, other):
		return term.factory.makeCons(
			term.head, 
			self.visit(term.tail, other),
			term.annotations
		)

extend = Extend().visit


def append(term, other):
	return extend(term, term.factory.makeCons(other, term.factory.makeNil()))


class Insert(Operation):
	
	def visitNil(self, term, index, other):
		if index == 0:
			return term.factory.makeCons(other, term)
		else:
			raise IndexError('index out of bounds')
	
	def visitCons(self, term, other):
		if index == 0:
			return term.factory.makeCons(other, term)
		else:
			return term.factory.makeCons(
				term.head,
				self.visit(term.tail, index - 1, other),
				term.annotations,
			)

insert = Insert().visit


class Reverse(Operation):
	'''Reverse a list term.'''
	
	def __call__(self, term):
		return self.visit(term, term.factory.makeNil())
		
	def visitNil(self, term, accum):
		return accum
		
	def visitCons(self, term, accum):
		return self.visit(
			term.tail,
			term.factory.makeCons(term.head, accum),
		)
		
reverse = Reverse()