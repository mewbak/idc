'''List term operations.'''


from aterm import types
from aterm import visitor


# FIXME: write non-recursive versions


class _Operation(visitor.Visitor):
	'''Base visitor class for list operations.'''

	def visitTerm(self, term, *args, **kargs):
		raise TypeError('not a list term', term)


def empty(term):
	'''Whether a list term is empty or not.'''
	return types.isNil(term)


def length(term):
	'''Length of a list term.'''
	length = 0
	while not types.isNil(term):
		assert types.isCons(term)
		length += 1
		term = term.tail
	return length


def item(term, index):
	'''Get item at given index of a list term.'''
	if index < 0:
		raise IndexError('index out of bounds')
	while True:
		if types.isNil(term):
			raise IndexError('index out of bounds')
		if not types.isCons(term):
			raise TypeError('not a list term', term)
		if index == 0:
			return term.head
		index -= 1
		term = term.tail


class Iter(_Operation):
	'''List term iterator.'''

	def __init__(self, term):
		_Operation.__init__(self)
		self.term = term

	def next(self):
		return self.visit(self.term)

	def visitNil(self, term):
		raise StopIteration

	def visitCons(self, term):
		head = term.head
		self.term = term.tail
		return head


class _Extend(_Operation):

	def __init__(self, other):
		_Operation.__init__(self)
		self.other = other

	def visitNil(self, term):
		return self.other

	def visitCons(self, term):
		return term.factory.makeCons(term.head, self.visit(term.tail))

def extend(term, other):
	'''Return the concatenation of two list terms.'''
	return _Extend(other).visit(term)


def append(term, other):
	'''Append an element to a list.'''
	return extend(term, term.factory.makeCons(other, term.factory.makeNil()))


class _Insert(_Operation):

	def visitNil(self, term, index, other):
		if index == 0:
			return term.factory.makeCons(other, term)
		else:
			raise IndexError('index out of bounds')

	def visitCons(self, term, index, other):
		if index == 0:
			return term.factory.makeCons(other, term)
		else:
			return term.factory.makeCons(
				term.head,
				self.visit(term.tail, index - 1, other),
			)

def insert(term, index, other):
	'''_Insert an element into the list.'''
	return _Insert().visit(index, other)


class _Reverse(_Operation):

	def __call__(self, term):
		return self.visit(term, term.factory.makeNil())

	def visitNil(self, term, accum):
		return accum

	def visitCons(self, term, accum):
		return self.visit(
			term.tail,
			term.factory.makeCons(term.head, accum),
		)

def reverse(term):
	'''_Reverse a list term.'''
	return _Reverse().visit(term, term.factory.makeNil())



class _Filter(_Operation):

	def __init__(self, function):
		_Operation.__init__(self)
		self.function = function

	def visitNil(self, term):
		return term

	def visitCons(self, term):
		tail = self.visit(term.tail)
		if not self.function(term.head):
			return tail
		elif tail is term.tail:
			return term
		else:
			return term.factory.makeCons(term.head, tail)

def filter(function, term):
	"""Return a list term with the elements for which the function returns
	true."""
	filter = _Filter(function)
	return filter.visit(term)


class _Fetcher(_Operation):

	def __init__(self, function):
		_Operation.__init__(self)
		self.function = function

	def visitNil(self, term):
		return None

	def visitCons(self, term):
		if self.function(term.head):
			return term.head
		else:
			return self.visit(term.tail)

def fetch(function, term):
	"""Return a the first term of a list term for which the function returns
	true."""
	fetcher = _Fetcher(function)
	return fetcher.visit(term)


class _Splitter(visitor.Visitor):

	def __init__(self, index):
		visitor.Visitor.__init__(self)
		self.index = index

	def visitTerm(self, term, index):
		raise TypeError('not a term list', term)

	def visitNil(self, term, index):
		if index == self.index:
			return term.factory.makeNil(), term
		else:
			raise IndexError('index out of range')

	def visitCons(self, term, index):
		if index == self.index:
			return term.factory.makeNil(), term
		else:
			head, tail = self.visit(term.tail, index + 1)
			return term.factory.makeCons(
				term.head,
				head,
			), tail

def split(term, index):
	'''Splits a list term in two lists.
	The argument is the index of the first element of the second list.
	'''
	splitter = _Splitter(index)
	return splitter.visit(term, 0)
