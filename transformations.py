'''Term transformation framework. It is inspired on the Stratego/XT 
framework. More information available at 
http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/
'''


# pylint: disable-msg=W0142


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


class Adaptor(Transformation):
	'''Transformation adapter for a regular function.'''
	
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
	

class Fail(Transformation):
	'''Failure transformation.'''
	
	def __call__(self, term):
		raise Failure


class Unary(Transformation):
	'''Base class for unary operations on transformations.'''
	
	def __init__(self, operand):
		Transformation.__init__(self)
		self.operand = operand


class Not(Unary):
	'''Fail if a transformation applies.'''
	
	def __call__(self, term):
		try:
			self.operand(term)
		except Failure:
			return term
		else:
			raise Failure


class Try(Unary):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	def __call__(self, term):
		try:
			return self.operand(term)
		except Failure:
			return term


class Binary(Transformation):
	'''Base class for binary operations on transformations.'''
	
	def __init__(self, loperand, roperand):
		Transformation.__init__(self)
		self.loperand = loperand
		self.roperand = roperand


class Or(Binary):
	'''Attempt the first transformation, transforming the second on failure.'''
	
	def __call__(self, term):
		try:
			return self.loperand(term)
		except Failure:
			return self.roperand(term)


class And(Binary):
	'''Transformation composition.'''
	
	def __call__(self, term):
		return self.roperand(self.loperand(term))


# TODO: write decorators for transformations


class Traverser(Visitor, Unary):
	'''Base class for all term traversers.'''

	def __init__(self, operand):
		Visitor.__init__(self)
		Unary.__init__(self, operand)
	

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
	'''Applies a transformation to all elements of a list term.'''

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
	'''Traverses a list until it finds a element for which the transformationormation 
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
	'''Applies a transformation to each element of a list, keeping only the 
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
	'''Applies a transformation to all subterms of a term.'''

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


class Proxy(Unary):
	
	def __call__(self, term):
		return self.operand(term)


def BottomUp(operand):
	result = Proxy(None)
	result.operand = And(All(result), operand)
	return result


def TopDown(operand):
	result = Proxy(None)
	result.operand = And(operand, All(result))
	return result


def InnerMost(operand):
	result = Proxy(None)
	result.operand = BottomUp(Try(And(operand, result)))
	return result


# TODO: pre-parse the patterns


class Match(Transformation):
	
	def __init__(self, pattern):
		self.pattern = pattern

	def __call__(self, term):
		factory = term.factory
		if factory.match(self.pattern, term):
			return term
		else:
			return Failure		


class Rule(Transformation):
	
	def __init__(self, matchpat, buildpat):
		self.match = matchpat
		self.build = buildpat
	
	def __call__(self, term):
		factory = term.factory
		args = []
		kargs = {}
		if factory.match(self.match, term, args, kargs):
			return factory.make(self.build, *args, **kargs)
		else:
			return Failure


# TODO: write a MatchSet, BuildSet, RuleSet

