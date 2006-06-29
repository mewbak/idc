'''Path transformations.

A path is a term comprehending a list of integer indexes which indicate the
position of a term relative to the root term. The indexes are listed orderly
from the leaves to the root.
'''

	
import aterm.factory
import aterm.visitor

import paths

from transf import exception
from transf import base
from transf import operate
from transf import build
from transf import annotation


_factory = aterm.factory.factory
_path = _factory.parse('Path(_)')


get = annotation.Get('Path')


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
		return paths.annotate(term, root, func)

annotate = Annotate(base.ident, build.nil)


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
		return paths.project(term, path)
	
fetch = paths.project


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
		return paths.transform(term, path, func)
	

split = paths.split


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
		head, rest = paths.split(term, self.start)
		old_body, tail = paths.split(rest, self.end - self.start)
		
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


class Index(base.Transformation):
	
	def __init__(self, index):
		base.Transformation.__init__(self)
		self.index = index
		
	def apply(self, term, ctx):
		index = self.index.apply(term, ctx)
		if index.type != aterm.types.INT:
			raise exception.Fatal('index not integer', index)
		index = index.value
		if term.type == aterm.types.APPL:
			term = term.args
		while True:
			if term.type == aterm.types.NIL:
				raise exception.Failure('index out of range', index)
			elif term.type == aterm.LIST:
				if index == 0:
					return term.head
				else:
					term = term.tail
			else:
				raise exception.Failure('not a list term', term)
		

class Equals(operate.Unary):
	
	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		if paths.equals(term, ref):
			return term
		else:
			raise exception.Failure


class Contains(operate.Unary):
	
	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		if paths.contains(term, ref):
			return term
		else:
			raise exception.Failure


class Contained(operate.Unary):
	
	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		if paths.contained(term, ref):
			return term
		else:
			raise exception.Failure

