'''Term paths.'''


from aterm.factory import factory
from aterm import types
from aterm import visitor
from aterm import project


PRECEDENT = -2
ANCESTOR = -1
EQUAL = 0
DESCENDENT = 1
SUBSEQUENT = 2


class _Transformer(visitor.IncrementalVisitor):

	def __init__(self, index, func):
		visitor.IncrementalVisitor.__init__(self)
		self.index = index
		self.func = func

	def __call__(self, term):
		return self.visit(term, 0)

	def visitTerm(self, term, index):
		raise TypeError('not a term list or application', term)

	def visitNil(self, term, index):
		raise IndexError('index out of range', index)

	def visitHead(self, term, index):
		if index == self.index:
			return self.func(term)
		else:
			return term

	def visitTail(self, term, index):
		if index >= self.index:
			return term
		else:
			return self.visit(term, index + 1)

	def visitAppl(self, term, index):
		old_arg = term.args[self.index]
		new_arg = self.func(old_arg)
		if new_arg is not old_arg:
			args = list(term.args)
			args[self.index] = new_arg
			return term.factory.makeAppl(term.name, args, term.annotations)
		else:
			return term


class Path(object):
	'''A path is a term comprehending a list of integer indexes which indicate
	the position of a term relative to the root term.

	When a path is read/written to a string/list, indexes are listed ordely from
	the root to the leaves. However, when a path is read/written to a term, the
	indexes are from the leaves to the root, to take advantage of the maximal
	sharing.
	'''

	__slots__ = ['indices']

	def __init__(self, indices):
		self.indices = indices

	def compare(self, other):
		'''Rich path comparison.'''
		assert isinstance(other, Path)
		otherit = iter(other.indices)
		for selfelm in iter(self.indices):
			try:
				otherelm = otherit.next()
			except StopIteration:
				return ANCESTOR

			if otherelm < selfelm:
				return PRECEDENT
			if otherelm > selfelm:
				return SUBSEQUENT

		try:
			otherit.next()
		except StopIteration:
			pass
		else:
			return DESCENDENT

		return EQUAL

	def equals(self, other):
		return self.compare(other) == EQUAL

	__eq__ = equals

	def contains(self, other):
		return self.compare(other) in (DESCENDENT, EQUAL)

	def contained(self, other):
		return self.compare(other) in (ANCESTOR, EQUAL)

	def contains_range(self, start, end):
		return self.contains(start) and self.contains(self, end)

	def contained_in_range(self, start, end):
		return (
			self.compare(start) in (ANCESTOR, EQUAL, PRECEDENT) and
			self.compare(end) in (ANCESTOR, EQUAL, SUBSEQUENT)
		)

	def ancestor(self, other):
		'''Find the common ancestor of two paths.'''
		res = []
		for i1, i2 in zip(self.indices, other.indices):
			if i1 != i2:
				break
			res.append(i1)
		return Path(res)

	def project(self, term):
		'''Projects the subterm specified by a path.'''
		for index in self.indices:
			term = project.subterm(term, index)
		return term

	def transform(self, term, func):
		func = func
		for index in reversed(self.indices):
			func = _Transformer(index, func)
		term = func(term)
		return term

	def fromTerm(cls, trm):
		res = []
		tail = trm
		while tail.type != types.NIL:
			if tail.type != types.CONS:
				raise ValueError('bad path', trm)
			idx = tail.head
			if idx.type != types.INT:
				raise ValueError('bad index', idx)
			res.append(idx.value)
			tail = tail.tail
		res.reverse()
		return cls(res)
	fromTerm = classmethod(fromTerm)

	def toTerm(self):
		res = factory.makeNil()
		for index in self.indices:
			res = factory.makeCons(factory.makeInt(index), res)
		return res

	def fromStr(cls, s):
		res = [int(x) for x in s.split('/') if x != '']
		return cls(res)
	fromStr = classmethod(fromStr)

	def toStr(self):
		return '/' + ''.join([str(elm) + '/' for elm in self.indices])

	__str__ = toStr


class _Annotator(visitor.IncrementalVisitor):

	_path = 'Path(_)'

	def __init__(self, func = None):
		visitor.IncrementalVisitor.__init__(self)
		if func is None:
			self.func = lambda term: True
		else:
			self.func = func

	def visit(self, term, path, index):
		term = visitor.IncrementalVisitor.visit(self, term, path, index)
		if self.func(term):
			return term.setAnnotation(self._path, term.factory.make(self._path, path))
		else:
			return term

	def visitTerm(self, term, path, index):
		return term

	def visitHead(self, term, path, index):
		path = term.factory.makeCons(term.factory.makeInt(index), path)
		return self.visit(term, path, 0)

	def visitTail(self, term, path, index):
		# no need to annotate tails
		return visitor.IncrementalVisitor.visit(self, term, path, index + 1)

	def visitAppl(self, term, path, index):
		return term.factory.makeAppl(
			term.name,
			[self.visit(
					arg,
					term.factory.makeCons(term.factory.makeInt(index), path),
					0
				) for index, arg in zip(range(len(term.args)), term.args)
			],
			term.annotations,
		)

def annotate(term, root = None, func = None):
	'''Recursively annotates the terms and all subterms with their
	path.'''
	annotator = _Annotator(func)
	if root is None:
		root = term.factory.makeNil()
	return annotator.visit(term, root, 0)
