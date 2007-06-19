'''List term operations.'''


from aterm import visitor


class _Operation(visitor.Visitor):
	'''Base visitor class for list operations.'''

	def visitTerm(self, term, *args, **kargs):
		return TypeError('not a list term', term)


class _Empty(_Operation):

	def visitNil(self, term):
		return True

	def visitCons(self, term):
		return False

def empty(term):
	'''Whether a list term is empty or not.'''
	return _Empty().visit(term)


class _Length(_Operation):

	def visitNil(self, term):
		return 0

	def visitCons(self, term):
		return self.visit(term.tail) + 1

def length(term):
	'''_Length of a list term.'''
	return _Length().visit(term)


class _Item(_Operation):

	def visitNil(self, term, index):
		raise IndexError('index out of bounds')

	def visitCons(self, term, index):
		if index == 0:
			return term.head
		else:
			return self.visit(term.tail, index - 1)

def item(term, index):
	'''Get item at given index of a list term.'''
	return _Item().visit(term, index)


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

	def visitNil(self, term, other):
		return other

	def visitCons(self, term, other):
		return term.factory.makeCons(
			term.head,
			self.visit(term.tail, other)
		)

def extend(term, other):
	'''Return the concatenation of two list terms.'''
	return _Extend().visit(term, other)


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
