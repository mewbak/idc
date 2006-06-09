'''Path to sub-terms in an aterm.
'''


import aterm.factory
import aterm.visitor
import transf


_factory = aterm.factory.Factory()
_path = _factory.parse('Path(_)')

class Annotator(aterm.visitor.IncrementalVisitor):
	'''Annotate the term and sub-terms with their relative path.'''

	def __call__(self, term, path = None):
		if path is None:
			path = term.factory.makeNil()
		return self.visit(term, path, 0)
	
	def visit(self, term, path, index):
		term = super(Annotator, self).visit(term, path, index)
		return term.setAnnotation(_path, _path.make(path))
		
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

annotate = Annotator()


class IndexFetch(transf.base.Transformation, aterm.visitor.Visitor):
	'''Fetch a subterm.'''

	def __init__(self, index):
		transf.base.Transformation.__init__(self)
		aterm.visitor.Visitor.__init__(self)
		self.index = index

	def apply(self, term, context):
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


def PathFetch(path):
	'''Transformation which fetchs sub-term with the specified path.'''
	result = transf.base.ident
	for index in path:
		result = IndexFetch(int(index)) & result
	return result


def fetch(term, path):
	'''Fetches the sub-term with the specified path.'''
	return PathFetch(path)(term)


class Index(transf.base.Transformation, aterm.visitor.IncrementalVisitor):

	def __init__(self, operand, index):
		transf.base.Transformation.__init__(self)
		aterm.visitor.IncrementalVisitor.__init__(self)
		self.operand = operand
		self.index = index
		
	def apply(self, term, context):
		return self.visit(term, context, 0)
	
	def visitTerm(self, term, context, index):
		raise TypeError('not a term list or application: %r' % term)
	
	def visitNil(self, term, context, index):
		raise IndexError('index out of range')
	
	def visitHead(self, term, context, index):
		if index == self.index:
			return self.operand(term, context)
		else:
			return term
	
	def visitTail(self, term, context, index):
		if index < self.index:
			return self.visit(term, context, index + 1)
		else:
			return term

	def visitName(self, term, context, index):
		return term

	def visitArgs(self, term, context, index):
		return self.visit(term, context, index)


def Path(transformation, path):
	'''Apply a transformation only on the specified path.'''
	result = transformation
	for index in path:
		result = Index(result, int(index))
	return result


class _Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def __init__(self, index):
		'''The argument is the index of the first element of the second list.'''
		self.index = index

	def __call__(self, term):
		return self.visit(term, 0)
	
	def visitTerm(self, term, index):
		raise TypeError('not a term list: %r' % term)
	
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


def split(term, index):
	'''Split a term list in two.'''
	return _Splitter(index)(term)


class Range(transf.base.Transformation):
	'''Apply a transformation on a subterm range.'''

	def __init__(self, operand, start, end):
		'''Start and end indexes specify the subterms that will be transformed, 
		inclusively.
		'''
		transf.base.Transformation.__init__(self)
		self.operand = operand
		if start > end:
			raise ValueError('start index %r greater than end index %r' % (start, end))
		self.start = start
		self.end = end
		
	def apply(self, term, context):
		head, rest = split(term, self.start)
		old_body, tail = split(rest, self.end - self.start)
		
		new_body = self.operand(old_body, context)
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
	result = Path(result, start)
	return result

