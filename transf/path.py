'''Path transformations.

A path is a term comprehending a list of integer indexes which indicate the
position of a term relative to the root term. The indexes are listed orderly
from the leaves to the root.
'''

	
import aterm.factory
import aterm.visitor

from transf import exception
from transf import base
from transf import build
from transf import annotation


_factory = aterm.factory.factory
_path = _factory.parse('Path(_)')


def reverse_path(path):
	res = _factory.makeNil()
	for index in path:
		res = _factory.makeCons(index, res)
	return res



def common_subpath(path1, path2):
	path1 = reverse_path(path1)
	path2 = reverse_path(path2)
	res = _factory.makeNil()
	while path1 and path2 and path1.head == path2.head:
		res = _factory.makeCons(path1.head)
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
		if func is not None:
			self.callback = func

	def callback(self, term):
		return True

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


class Annotate(base.Transformation):
	'''Transformation which annotates the path of terms and subterms for which the 
	supplied transformation succeeds.'''

	def __init__(self, operand = None, root = None):
		base.Transformation.__init__(self)
		if operand is None:
			self.operand = base.ident
		else:
			self.operand = operand
		if root is None:
			self.root = build.nil
		elif isinstance(root, aterm.terms.Term):
			self.root = build.Term(root)
		else:
			self.root = root
		
	def apply(self, term, ctx):
		root = self.root.apply(term, ctx)
		def func(term):
			try:
				self.operand.apply(term, ctx)
			except exception.Failure:
				return False
			else:
				return True
		return Annotator.annotate(term, root, func)


annotate = Annotate(base.ident, build.nil)


get = annotation.Get('Path')


class Projector(aterm.visitor.Visitor):
	'''Visitor which projects a subterm along a path.'''

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


class Project(base.Transformation):
	'''Projects a subterm along a path.'''

	def __init__(self, path):
		base.Transformation.__init__(self)
		if isinstance(path, aterm.terms.Term):
			self.path = build.Term(path)
		else:
			self.path = path

	def apply(self, term, ctx):
		path = self.path.apply(term, ctx)
		return Projector.project(term, path)
	

def fetch(term, path):
	'''Fetches the sub-term with the specified path.'''
	return Project(path)(term)


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


class SubTerm(base.Transformation):
	'''Projects a subterm along a path.'''

	def __init__(self, operand, path):
		base.Transformation.__init__(self)
		self.operand = operand
		if isinstance(path, aterm.terms.Term):
			self.path = build.Term(path)
		else:
			self.path = path

	def apply(self, term, ctx):
		path = self.path.apply(term, ctx)
		func = lambda term: self.operand.apply(term, ctx)
		return Transformer.transform(term, path, func)
	

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


class Range(base.Transformation):
	'''Apply a transformation on a subterm range.'''

	def __init__(self, operand, start, end):
		'''Start and end indexes specify the subterms that will be transformed, 
		inclusively.
		'''
		base.Transformation.__init__(self)
		self.operand = operand
		if start > end:
			raise ValueError('start index %r greater than end index %r' % (start, end))
		self.start = start
		self.end = end
		
	def apply(self, term, ctx):
		head, rest = split(term, self.start)
		old_body, tail = split(rest, self.end - self.start)
		
		new_body = self.operand.apply(old_body, ctx)
		if new_body is not old_body:
			return head.extend(new_body.extend(tail))
		else:
			return term
			
		
def PathRange(transformation, start, end):
	'''Apply a transformation on a path range. The tails of the start and end 
	paths should be equal.'''
	result = transformation
	result = Range(result, start[0], end[0])
	if start[1:] != end[1]:
		raise ValueError('start and end path tails differ: %r, %r' % start, end)
	result = SubTerm(result, start)
	return result

