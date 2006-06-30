
import aterm.visitor
import transf

from transf import exception
from transf import base

class _Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.operand = operand

	def visitTerm(self, term, ctx):
		raise TypeError('not a term list: %r' % term)
	
	def visitNil(self, term, ctx):
		raise exception.Failure
		
	def visitCons(self, term, ctx):
		try:
			head = self.operand.apply(term.head, ctx)
		except exception.Failure:
			head, body, tail = self.visit(term.tail, ctx)
			return head.insert(0, term.head), body, tail
		else:
			return term.factory.makeNil(), term.head, term.tail


class Split(base.Transformation):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.splitter = _Splitter(operand)

	def apply(self, term, ctx):
		return term.factory.makeList(self.splitter.visit(term, ctx))


class SplitBlock(base.Transformation):

	def __init__(self, name):
		self.name = name
		self.split_head = Split(
			transf.match.Appl(
				"Label", 
				[transf.match.Term(name)]
			)
		)
		self.split_tail = Split(
			transf.parse.Transf("?Ret(*)")
		)

	def apply(self, term, ctx):
		head, first, rest = self.split_head.apply(term, ctx)
		body, last, tail = self.split_tail.apply(rest, ctx)
		
		return term.factory.makeList([
			head,
			body.append(last).insert(0, first),
			tail
		])


class ExtractBlock(base.Transformation):
	
	def __init__(self, operand, name):
		self.split_block = SplitBlock(name)
		self.operand = operand
		
	def apply(self, term, ctx):
		head, body, tail = self.split_block.apply(term, ctx)
		body = self.operand.apply(body, ctx)
		return head.extend(body.extend(tail))

