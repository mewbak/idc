
import aterm.visitor

from transf import *


def Tail(operand):
	tail = Proxy()
	tail.subject = operand | Cons(Ident(), tail)
	return tail


class _Splitter(aterm.visitor.Visitor):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.operand = operand

	def visitTerm(self, term):
		raise TypeError('not a term list: %r' % term)
	
	def visitNil(self, term):
		raise Failure
		
	def visitCons(self, term):
		try:
			head = self.operand(term.head)
		except Failure:
			head, body, tail = self.visit(term.tail)
			return head.insert(0, term.head), body, tail
		else:
			return term.factory.makeNil(), term.head, term.tail


class Split(Transformation):
	'''Splits a list term in two lists.'''

	def __init__(self, operand):
		'''The argument is the index of the first element of the second list.'''
		self.splitter = _Splitter(operand)

	def __call__(self, term):
		return term.factory.makeList(self.splitter.visit(term))


class SplitBlock(Transformation):

	def __init__(self, name):
		self.name = name
		self.split_head = Split(
			Match("Label(name)", name=name)
		)
		self.split_tail = Split(
			Match("Ret(*)")
		)

	def __call__(self, term):
		head, first, rest = self.split_head(term)
		body, last, tail = self.split_tail(rest)
		
		return term.factory.makeList([
			head,
			body.append(last).insert(0, first),
			tail
		])


class ExtractBlock(Transformation):
	
	def __init__(self, operand, name):
		self.split_block = SplitBlock(name)
		self.operand = operand
		
	def __call__(self, term):
		head, body, tail = self.split_block(term)
		body = self.operand(body)
		return head.extend(body.extend(tail))

