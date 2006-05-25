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


class Evaluator(walker.Walker):
	"""Evaluates a path on a term."""
	
	def evaluate(cls, term, path):
		"""Class method which evaluates the given term."""
		return cls(term.factory).evaluate_term(term, path)
	evaluate = classmethod(evaluate)

	def evaluate_term(self, term, path):
		"""Recursively evaluates a term with paths relative to the given path."""
		
		if path.isEmpty():
			return term
		
		tail = path.getTail()		
		term = self.evaluate_term(term, tail)
		
		head = path.getHead()
		index = head.getValue()
		
		type_ = term.getType()
		if type_ == aterm.LIST:
			return term[index]
		elif type_ == aterm.APPL:
			return term.getArgs()[index]
		else:
			raise walker.Failure
		return term.setAnnotation(self.factory.parse("Path"), path)


class CoVisitor(aterm.visitor.Visitor):

	pass



class PathVisiXtor(aterm.visitor.Visitor):

	def __init__(self):
		factory = aterm.factory.Factory()
		self.path = factory.makeNil()
		self.index = 0
		
	def visitTerm(self, term):
		self.recurse = True
	
	def visitCons(self, term):
		self.visitTerm(term)
		if not self.recurse:
			return False
		
		path = self.path
		index = self.index
		
		factory = term.factory
		
		self.path = factory.makeCons(factory.makeInt(index), path)
		self.index = 0
		self.visit(term.getHead())
		
		self.path = path
		self.index = index + 1
		self.visit(term.getTail())
		
		assert path == self.path.getTail()
		
		self.path = path
		self.index = index
	
	def visitAppl(self, term):
		self.visitTerm(term)
		if not self.recurse:
			return False
		
		self.visit(term.getArgs())		


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
	for pathitem in path:
		result = Range(result, pathitem, pathitem)
	return result


def SubPathRange(transformation, start, end):
	'''Apply a transformation on a path range. The tails of the start and end 
	paths should be equal.'''
	result = transformation
	result = Range(result, start[0], end[0])
	if start[1:] != end[1]:
		raise ValueError('start and end path tails differ: %r, %r' % start, end)
	result = Path(result, start)
	return result

