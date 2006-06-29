'''Paths into terms.

A path is a term comprehending a list of integer indexes which indicate the
position of a term relative to the root term. The indexes are listed orderly
from the leaves to the root.
'''


# TODO: Write a dedicated class instead to replace these statements

import aterm.factory
import aterm.visitor

_factory = aterm.factory.factory
_path = _factory.parse('Path(_)')


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

	def annotate(cls, term, root = None, func = None):
		annotator = cls(func)
		if root is None:
			root = term.factory.makeNil()
		return annotator.visit(term, root, 0)
	annotate = classmethod(annotate)
		
	def __init__(self, func = None):
		super(Annotator, self).__init__()
		if func is None:
			self.callback = lambda term: True
		else:
			self.callback = func

	def visit(self, term, path, index):
		term = super(Annotator, self).visit(term, path, index)
		if self.callback(term):
			return term.setAnnotation(_path, _path.make(path))
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

	def visitName(self, term, path, index):
		return term

	def visitArgs(self, term, path, index):
		# no need to annotate arg lists
		return super(Annotator, self).visit(term, path, index)

annotate = Annotator.annotate


class Projector(aterm.visitor.Visitor):
	'''Visitor which projects the subterm specified by a path.'''

	def project(cls, term, path):
		projector = cls()
		return projector.visit(term, reverse_path(path), 0)
	project = classmethod(project)

	def visit(self, term, path, index):
		if not path:
			return term
		else:
			return super(Projector, self).visit(term, path, index)
	
	def visitTerm(self, term, path, index):
		raise TypeError('not a term list or application', term)
	
	def visitNil(self, term, path, index):
		raise IndexError('index out of range', index)
		
	def visitCons(self, term, path, index):
		if index == path.head.value:
			return self.visit(term.head, path.tail, 0)
		else:
			return self.visit(term.tail, path, index + 1)

	def visitAppl(self, term, path, index):
		return self.visit(term.args, path, index)



class Transformer(aterm.visitor.IncrementalVisitor):

	def transform(cls, term, path, func):
		transformer = cls(func)
		return transformer.visit(term, reverse_path(path), 0)
	transform = classmethod(transform)
		
	def __init__(self, func):
		super(Transformer, self).__init__()
		self.callback = func

	def visit(self, term, path, index):
		if not path:
			return self.callback(term)
		else:
			return super(Transformer, self).visit(term, path, index)
	
	def visitTerm(self, term, path, index):
		raise TypeError('not a term list or application', term)
	
	def visitNil(self, term, path, index):
		raise IndexError('index out of range', index)
		
	def visitHead(self, term, path, index):
		if index == path.head.value:
			return self.visit(term, path.tail, 0)
		else:
			return term
		
	def visitTail(self, term, path, index):
		if index == path.head.value:
			return term
		else:
			return self.visit(term, path, index + 1)
	
	def visitName(self, term, path, index):
		return term
	
	def visitArgs(self, term, path, index):
		return self.visit(term, path, 0)


class Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def split(cls, term, index):
		splitter = cls(index)
		return splitter.visit(term, 0)
	split = classmethod(split)
		
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
			head, tail = self.visit(term.getTail(), index + 1)
			return term.factory.makeCons(term.getHead(), head, term.getAnnotations()), tail


split = Splitter.split


class IndexProjector(aterm.visitor.Visitor):
	'''Visitor which projects the subterm specified by a path.'''

	def project(cls, term, index):
		projector = cls(index)
		return projector.visit(term, 0)
	project = classmethod(project)
	
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
		return self.visit(term.args, index)


def project(term, path):
	path = _reverse(path)
	while path:
		index = path.head.value
		term = IndexProjector.project(term, index)
		path = path.tail
	return term


class IndexTransformer(aterm.visitor.IncrementalVisitor):

	def __init__(self, index, func):
		aterm.visitor.IncrementalVisitor.__init__(self)
		self.index = index
		self.callback = func

	def __call__(self, term):
		return self.visit(term, 0)

	def visitTerm(self, term, index):
		raise TypeError('not a term list or application', term)
	
	def visitNil(self, term, index):
		raise IndexError('index out of range', index)
		
	def visitHead(self, term, index):
		if index == self.index:
			return self.callback(term)
		else:
			return term
		
	def visitTail(self, term, index):
		if index >= self.index:
			return term
		else:
			return self.visit(term, index + 1)
	
	def visitName(self, term, index):
		return term
	
	def visitArgs(self, term, index):
		return self.visit(term, 0)


def transform(term, path, func):
	func = func
	while path:
		index = path.head.value
		func = IndexTransformer(index, func)
		path = path.tail
	term = func(term)
	return term


class IndexSplitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def split(cls, term, index):
		splitter = cls(index)
		return splitter.visit(term, 0)
	split = classmethod(split)
		
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
			head, tail = self.visit(term.getTail(), index + 1)
			return term.factory.makeCons(term.getHead(), head, term.getAnnotations()), tail


import unittest

class TestPath(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.factory.factory
		
	def checkTransformation(self, func, testCases):
		for termStr, pathStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = func(term, _path)
			
			self.failUnlessEqual(result, expectedResult)
		
	def testAnnotate(self):
		self.checkTransformation(
			annotate,
			(
				('1', '[]', '1{Path([])}'),
				('[1,2]', '[]', '[1{Path([0])},2{Path([1])}]{Path([])}'),
				('C(1,2)', '[]', 'C(1{Path([0])},2{Path([1])}){Path([])}'),
				('[[[]]]', '[]', '[[[]{Path([0,0])}]{Path([0])}]{Path([])}'),
				('C(C(C))', '[]', 'C(C(C{Path([0,0])}){Path([0])}){Path([])}'),
				('[[1],[2]]', '[]', '[[1{Path([0,0])}]{Path([0])},[2{Path([0,1])}]{Path([1])}]{Path([])}'),
				('C(C(1),C(2))', '[]', 'C(C(1{Path([0,0])}){Path([0])},C(2{Path([0,1])}){Path([1])}){Path([])}'),
			)
		)

	projectTestCases = [
		('1', '[]', '1'),
		('[1,2]', '[]', '[1,2]'),
		('[1,2]', '[0]', '1'),
		('[1,2]', '[1]', '2'),
		('C(1,2)', '[]', 'C(1,2)'),
		('C(1,2)', '[0]', '1'),
		('C(1,2)', '[1]', '2'),
		('A([B,C],[D,E])', '[0,0]', 'B'),
		('A([B,C],[D,E])', '[1,0]', 'C'),
		('A([B,C],[D,E])', '[0,1]', 'D'),
		('A([B,C],[D,E])', '[1,1]', 'E'),
	]

	def testProject(self):
		self.checkTransformation(
			project, 
			self.projectTestCases
		)
	
	transformTestCases = [
		('1', '[]', 'X(1)'),
		('[1,2]', '[]', 'X([1,2])'),
		('[1,2]', '[0]', '[X(1),2]'),
		('[1,2]', '[1]', '[1,X(2)]'),
		('C(1,2)', '[]', 'X(C(1,2))'),
		('C(1,2)', '[0]', 'C(X(1),2)'),
		('C(1,2)', '[1]', 'C(1,X(2))'),
		('A([B,C],[D,E])', '[0,1]', 'A([B,C],[X(D),E])'),
		('A([B,C],[D,E])', '[1,0]', 'A([B,X(C)],[D,E])'),
	]	
	
	def testTransform(self):
		self.checkTransformation(
			lambda t, p: transform(t, p, lambda x: x.factory.make('X(_)', x)),
			self.transformTestCases
		)

	splitTestCases = [
		('[0,1,2,3]', 0, '[]', '[0,1,2,3]'),
		('[0,1,2,3]', 1, '[0,]', '[1,2,3]'),
		('[0,1,2,3]', 2, '[0,1,]', '[2,3]'),
		('[0,1,2,3]', 3, '[0,1,2,]', '[3]'),
		('[0,1,2,3]', 4, '[0,1,2,3]', '[]'),
	]
	
	def testSplit(self):
		for inputStr, index, expectedHeadStr, expectedTailStr in self.splitTestCases:
			input = self.factory.parse(inputStr)
			expectedHead = self.factory.parse(expectedHeadStr)
			expectedTail = self.factory.parse(expectedTailStr)
			
			head, tail = split(input, index)
			
			self.failUnlessEqual(head, expectedHead)
			self.failUnlessEqual(tail, expectedTail)

	rangeTestCases = [
		('[0,1,2]', 0, 0, '[0,1,2]'),
		('[0,1,2]', 0, 1, '[X(0),1,2]'),
		('[0,1,2]', 0, 2, '[X(0),X(1),2]'),
		('[0,1,2]', 0, 3, '[X(0),X(1),X(2)]'),
		('[0,1,2]', 1, 1, '[0,1,2]'),
		('[0,1,2]', 1, 2, '[0,X(1),2]'),
		('[0,1,2]', 1, 3, '[0,X(1),X(2)]'),
		('[0,1,2]', 2, 2, '[0,1,2]'),
		('[0,1,2]', 2, 3, '[0,1,X(2)]'),
		('[0,1,2]', 3, 3, '[0,1,2]'),
	]	
	
	def testRange(self):
		for inputStr, start, end, expectedResultStr in self.rangeTestCases:
			input = self.factory.parse(inputStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Range(lists.Map(rewrite.Pattern('x', 'X(x)')), start, end)(input)
			
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
