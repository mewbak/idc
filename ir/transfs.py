
import aterm.visitor
import transf

from transf import exception
from transf import base

class _Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.operand = operand

	def visitTerm(self, term, context):
		raise TypeError('not a term list: %r' % term)
	
	def visitNil(self, term, context):
		raise exception.Failure
		
	def visitCons(self, term, context):
		try:
			head = self.operand(term.head, context)
		except exception.Failure:
			head, body, tail = self.visit(term.tail, context)
			return head.insert(0, term.head), body, tail
		else:
			return term.factory.makeNil(), term.head, term.tail


class Split(base.Transformation):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.splitter = _Splitter(operand)

	def apply(self, term, context):
		return term.factory.makeList(self.splitter.visit(term, context))


class SplitBlock(base.Transformation):

	def __init__(self, name):
		self.name = name
		self.split_head = Split(
			transf.match.MatchAppl(
				"Label", 
				[transf.match.MatchPattern(name)]
			)
		)
		self.split_tail = Split(
			transf.match.MatchPattern("Ret(*)")
			# FIXME: not working?
			#_f.Ret()
		)

	def apply(self, term, context):
		head, first, rest = self.split_head.apply(term, context)
		body, last, tail = self.split_tail.apply(rest, context)
		
		return term.factory.makeList([
			head,
			body.append(last).insert(0, first),
			tail
		])


class ExtractBlock(base.Transformation):
	
	def __init__(self, operand, name):
		self.split_block = SplitBlock(name)
		self.operand = operand
		
	def apply(self, term, context):
		head, body, tail = self.split_block.apply(term, context)
		body = self.operand(body, context)
		return head.extend(body.extend(tail))

