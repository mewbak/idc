"""Path to sub-terms in an aterm.
"""

import aterm
import aterm.visitor
import walker
import transformations


class Annotator(aterm.visitor.IncrementalVisitor,object):
	'''Apply a transformation on a subterm range.'''

	def __call__(self, term, path = None):
		if path is None:
			path = term.factory.makeNil()
		return self.visit(term, path, 0)
	
	def visit(self, term, path, index):
		term = super(Annotator, self).visit(term, path, index)
		return term.setAnnotation(term.factory.parse('Path'), path)
		
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


class Index(aterm.visitor.Visitor):
	'''Fetch a subterm.'''

	def __init__(self, index):
		self.index = index

	def __call__(self, term):
		return self.visit(term, 0)
	
	def visitTerm(self, term, index):
		raise TypeError('not a term list or application: %r' % term)
	
	def visitNil(self, term, index):
		raise IndexError('index out of range')
		
	def visitCons(self, term, index):
		if index == self.index:
			return term.getHead()
		else:
			return self.visit(term.getTail(), index + 1)

	def visitAppl(self, term, index):
		return self.visit(term.getArgs(), index)


def Evaluator(path):
	'''Apply a transformation only on the specified path.'''
	result = transformations.Ident()
	for index in path:
		result = transformations.And(Index(int(index)),result)
	return result


class Range(aterm.visitor.IncrementalVisitor):
	'''Apply a transformation on a subterm range.'''

	def __init__(self, operand, start, end):
		'''Start and end indexes specify the subterms that will be transformed, 
		inclusively.
		'''
		self.operand = operand
		self.start = start
		self.end = end

	def __call__(self, term):
		return self.visit(term, 0)
	
	def visitTerm(self, term, index):
		raise TypeError('not a term list or application: %r' % term)
	
	def visitHead(self, term, index):
		if self.start <= index <= self.end:
			return self.operand(term)
		else:
			return term
	
	def visitTail(self, term, index):
		if index < self.end:
			return self.visit(term, index + 1)
		else:
			return term		

	def visitName(self, term, index):
		return term

	def visitArgs(self, term, index):
		return self.visit(term, index)


def Path(transformation, path):
	'''Apply a transformation only on the specified path.'''
	result = transformation
	for index in path:
		result = Range(result, index, index)
	return result


def PathRange(transformation, start, end):
	'''Apply a transformation on a path range. The tails of the start and end 
	paths should be equal.'''
	result = transformation
	result = Range(result, start[0], end[0])
	if start[1:] != end[1]:
		raise ValueError('start and end path tails differ: %r, %r' % start, end)
	result = Path(result, start)
	return result

