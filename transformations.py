'''Term transformation framework. It is inspired on the Stratego/XT 
framework. More information available at 
http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/
'''


import aterm
from aterm.visitor import Visitor


class Failure(Exception):
	'''Transformation failed to apply.'''

	# TODO: keep a reference to the failure provoking term
	
	pass


class Transformation:
	'''Base class for transformations. Although convenient, it is not necessary 
	for every transformation to derive from this class. Generally, a regular function 
	can be used instead.
	'''
	
	def __init__(self):
		pass
	
	def __call__(self, term):
		raise NotImplementedError

	def __not__(self):
		return Not(self)
	
	def __or__(self, other):
		return Or(self, other)

	def __ror__(self, other):
		return Or(other, self)

	def __and__(self, other):
		return And(self, other)	

	def __rand__(self, other):
		return And(other, self)


class Wrapper(Transformation):
	'''Transformation wrapper around a regular function.'''
	
	def __init__(self, func, *args, **kargs):
		Transformation.__init__(self)
		self.func = func
		self.args = args
		self.kargs = kargs

	def __call__(self, term):
		return self.func(term, *self.args, **self.kargs)


class Ident(Transformation):
	'''Identity transformation.'''
	
	def __call__(self, term):
		return term
	
ident = Ident()


class Fail(Transformation):
	'''Failure transformation.'''
	
	def __call__(self, term):
		raise Failure

fail = Fail()


class UnaryOp(Transformation):
	'''Base class for unary operations on transformations.'''
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.operand = operand


class Not(UnaryOp):
	'''Fail if a transformation applies.'''
	
	def __call__(self, term):
		try:
			self.operand(term)
		except Failure:
			return term
		else:
			raise Failure


class Try(UnaryOp):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	def __call__(self, term):
		try:
			return self.operand(term)
		except Failure:
			return term


class BinaryOp(Transformation):
	'''Base class for binary operations on transformations.'''
	
	def __init__(self, loperand, roperand):
		Transformation.__init__(self)
		self.loperand = loperand
		self.roperand = roperand


class Or(BinaryOp):
	'''Attempt the first transformation, transforming the second on failure.'''
	
	def __call__(self, term):
		try:
			return self.loperand(term)
		except Failure:
			return self.roperand(term)


class And(BinaryOp):
	'''Transformation composition.'''
	
	def __call__(self, term):
		return self.roperand(self.loperand(term))


# TODO: write decorators for transformations


class Traverser(Visitor, UnaryOp):
	'''Base class for all term traversers.'''

	def __init__(self, operand):
		Visitor.__init__(self)
		UnaryOp.__init__(self, operand)
	

class ListTraverser(Traverser):
	'''Base class for list traversers.'''
	
	# TODO: extend to tuples too
	
	def visitNil(self, term):
		return term

	def visitHead(self, term):
		return self.operand(term)
	
	def visitTail(self, term):
		return self.visit(term)
	
	def visitPlaceholder(self, term):
		# placeholders are kept unmodified
		return term


class Map(ListTraverser):
	'''Applies a operandormation to all elements of a list term.'''

	def visitCons(self, term):
		old_head = term.getHead()
		old_tail = term.getTail()
		new_head = self.visitHead(old_head)
		new_tail = self.visitTail(old_tail)
		if new_head is not old_head or new_tail is not old_tail:
			annos = term.getAnnotations()
			return term.factory.makeCons(new_head, new_tail, annos)
		else:
			return term


class Fetch(ListTraverser):
	'''Traverses a list until it finds a element for which the operandormation 
	succeeds and then stops. That element is the only one that is operandormed.
	'''
	
	def visitNil(self, term):
		raise Failure('fetch reached the end of the list')
	
	def visitCons(self, term):
		old_head = term.getHead()
		old_tail = term.getTail()
		
		try:
			new_head = self.visitHead(old_head)
		except Failure:
			new_head = old_head
			new_tail = self.visitTail(old_tail)
		else:
			new_tail = old_tail
			
		if new_head is not old_head or new_tail is not old_tail:
			annos = term.getAnnotations()
			return term.factory.makeCons(new_head, new_tail, annos)
		else:
			return term


class Filter(ListTraverser):
	'''Applies a operandormation to each element of a list, keeping only the 
	elements for which it succeeds.
	'''

	def visitCons(self, term):
		old_head = term.getHead()
		old_tail = term.getTail()
		new_tail = self.visitTail(old_tail)
		
		try:
			new_head = self.visitHead(old_head)
		except Failure:
			return new_tail
			
		if new_head is not old_head or new_tail is not old_tail:
			annos = term.getAnnotations()
			return term.factory.makeCons(new_head, new_tail, annos)
		else:
			return term


class All(Traverser):
	'''Applies a function to all subterms of a term.'''

	def __init__(self, operand):
		Traverser.__init__(self, operand)
		self.operand_map = Map(operand)

	def visitTerm(self, term):
		# terms other than applications are kept unmodified
		return term

	def visitAppl(self, term):
		old_args = term.getArgs()
		new_args = self.operand_map(old_args)
		if new_args is not old_args:
			name = term.getName()
			annos = term.getAnnotations()
			return term.factory.makeAppl(name, new_args, annos)
		else:
			return term


class BottomUp(Transformation):
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.__call__ = All(self) & operand


class TopDown(Transformation):
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.__call__ = operand & All(self)


class InnerMost(Transformation):
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.__call__ = BottumpUp(Try(operand & self))


def main():
	
	def test(term):
		return term.factory.make("X(_)", term)
	
	def pos(term):
		if term.getType() == aterm.INT and term.getValue() > 0:
			return test(term)
		else:
			raise Failure

	factory = aterm.Factory()

	print Map(test)(factory.make("[1, 2, 3, 4]"))
	print Filter(pos)(factory.make("[-1, 0, 1, 2]"))
	print Fetch(pos)(factory.make("[-1, 0, 1, 2]"))
	print All(test)(factory.make("C(1, 2, 3, 4)"))


if __name__ == '__main__':
    main()