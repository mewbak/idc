'''Term paths.

A path is a term comprehending a list of integer indexes which indicate the
position of a term relative to the root term. The indexes are listed orderly
from the leaves to the root.
'''


import aterm.factory
import aterm.visitor

_factory = aterm.factory.factory
_path = 'Path(_)'


PRECEDENT = -2
ANCESTOR = -1
EQUAL = 0
DESCENDENT = 1
SUBSEQUENT = 2


class Path(object):

	__slots__ = ['indices']

	def __init__(self, indices):
		self.indices = indices

	def compare(self, other):
		'''Rich path comparison.'''
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
		return compare(self, other) == EQUAL

	def contains(self, other):
		return compare(self, other) in (DESCENDENT, EQUAL)

	def contained(self, other):
		return compare(self, other) in (ANCESTOR, EQUAL)

	def contains_range(self, start, end):
		return contains(self, start) and contains(self, end)

	def contained_in_range(self, start, end):
		return (
			compare(self, start) in (ANCESTOR, EQUAL, PRECEDENT) and
			compare(self, end) in (ANCESTOR, EQUAL, SUBSEQUENT)
		)

	@classmethod
	def fromTerm(cls, trm):
		res = []
		tail = trm
		while tail.type != aterm.types.NIL:
			if tail.type != aterm.types.CONS:
				raise ValueError('bad path', trm)
			idx = tail.head
			if idx.type != aterm.types.INT:
				raise ValueError('bad index', idx)
			res.append(idx.value)
			tail = tail.tail
		return res

	def toTerm(self):
		return _factory.makeList(self.indices)

	@classmethod
	def fromStr(cls, s):
		return [int(x) for x in s.split('/') if x != '']

	def toStr(self):
		return '/' + ''.join([str(elm) + '/' for elm in self.indices])

	__str__ = toStr


def check(path):
	if path.type == aterm.types.NIL:
		return True
	if path.type == aterm.types.CONS:
		return path.head.type == aterm.types.INT and path.head.value >= 0 and check(path.tail)
	return False


def _reverse(path):
	res = _factory.makeNil()
	tail = path
	while tail.type != aterm.types.NIL:
		if tail.type != aterm.types.CONS:
			raise ValueError('bad path', path)
		idx = tail.head
		if idx.type != aterm.types.INT:
			raise ValueError('bad index', idx)
		res = _factory.makeCons(idx, res)
		tail = tail.tail
	return res


PRECEDENT = -2
ANCESTOR = -1
EQUAL = 0
DESCENDENT = 1
SUBSEQUENT = 2


def compare(path, ref_path):
	'''Rich path comparison.'''
	path = _reverse(path)
	ref_path = _reverse(ref_path)
	while ref_path:
		if not path:
			return ANCESTOR
		if path.head.value < ref_path.head.value:
			return PRECEDENT
		if path.head.value > ref_path.head.value:
			return SUBSEQUENT
		path = path.tail
		ref_path = ref_path.tail
	if path:
		return DESCENDENT
	return EQUAL


def equals(path1, path2):
	return compare(path1, path2) == EQUAL


def contains(path, subpath):
	return compare(path, subpath) in (ANCESTOR, EQUAL)


def contained(subpath, path):
	return compare(subpath, path) in (DESCENDENT, EQUAL)


def contains_range(path, startpath, endpath):
	return contains(path, startpath) and contains(path, endpath)


def contained_in_range(subpath, startpath, endpath):
	return \
		compare(subpath, startpath) in (DESCENDENT, EQUAL, SUBSEQUENT) and \
		compare(subpath, endpath) in (DESCENDENT, EQUAL, PRECEDENT)


def ancestor(path1, path2):
	'''Find the common ancestor of two paths.'''
	path1 = _reverse(path1)
	path2 = _reverse(path2)
	res = _factory.makeNil()
	while path1 and path2 and path1.head == path2.head:
		res = _factory.makeCons(path1.head, res)
		path1 = path1.tail
		path2 = path2.tail
	return res




class Annotator(aterm.visitor.IncrementalVisitor):
	'''Visitor which recursively annotates the terms and all subterms with their
	path.'''

	@classmethod
	def annotate(cls, term, root = None, func = None):
		annotator = cls(func)
		if root is None:
			root = term.factory.makeNil()
		return annotator.visit(term, root, 0)

	def __init__(self, func = None):
		super(Annotator, self).__init__()
		if func is None:
			self.func = lambda term: True
		else:
			self.func = func

	def visit(self, term, path, index):
		term = super(Annotator, self).visit(term, path, index)
		if self.func(term):
			return term.setAnnotation(_path, term.factory.make(_path, path))
		else:
			return term

	def visitTerm(self, term, path, index):
		return term

	def visitHead(self, term, path, index):
		path = term.factory.makeCons(term.factory.makeInt(index), path)
		return self.visit(term, path, 0)

	def visitTail(self, term, path, index):
		# no need to annotate tails
		return super(Annotator, self).visit(term, path, index + 1)

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

annotate = Annotator.annotate




class Projector(aterm.visitor.Visitor):
	'''Visitor which projects the subterm specified by a path.'''

	@classmethod
	def project(cls, term, index):
		projector = cls(index)
		return projector.visit(term, 0)

	def __init__(self, index):
		aterm.visitor.Visitor.__init__(self)
		self.index = index

	def visitTerm(self, term, index):
		raise TypeError('not a term list or application', term)

	def visitNil(self, term, index):
		raise IndexError('index out of range', self.index, index)

	def visitCons(self, term, index):
		if index == self.index:
			return term.head
		else:
			return self.visit(term.tail, index + 1)

	def visitAppl(self, term, index):
		return term.args[self.index]


def project(term, path):
	path = _reverse(path)
	while path:
		index = path.head.value
		term = Projector.project(term, index)
		path = path.tail
	return term


class Transformer(aterm.visitor.IncrementalVisitor):

	def __init__(self, index, func):
		aterm.visitor.IncrementalVisitor.__init__(self)
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


def transform(term, path, func):
	func = func
	while path:
		index = path.head.value
		func = Transformer(index, func)
		path = path.tail
	term = func(term)
	return term


class Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	@classmethod
	def split(cls, term, index):
		splitter = cls(index)
		return splitter.visit(term, 0)

	def __init__(self, index):
		super(Splitter, self).__init__()
		'''The argument is the index of the first element of the second list.'''
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
				term.annotations
			), tail

split = Splitter.split

