'''Term traversal transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import combinators
from transf import matching


class TraverseCons(base.Transformation):
	
	def __init__(self, head, tail):
		'''Takes as argument the transformations to be applied to the list 
		head and tail.'''
		self.head = head
		self.tail = tail
		
	def apply(self, term, context):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure
		
		new_head = self.head.apply(old_head, context)
		new_tail = self.tail.apply(old_tail, context)
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


class FilterCons(TraverseCons):
	
	def apply(self, term, context):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure
		
		new_tail = self.tail.apply(old_tail, context)
		try:
			new_head = self.head.apply(old_head, context)
		except exception.Failure:
			return new_tail

		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


def _TraverseList(elms_iter, tail):
	try:
		elm = elms_iter.next()
	except StopIteration:
		return tail
	else:
		return TraverseCons(elm, _TraverseList(elms_iter, tail))


def TraverseList(elms, tail = None):
	'''Transformation which matches a term list. 
	
	@param elms: sequence of transformations to be applied to the elements
	@param tail: option transformation to be applied to the list tail; defaults 
	to matching the empty list
	'''
	if tail is None:
		tail = matching.MatchNil()
	return _TraverseList(iter(elms), tail)
	

class TraverseAppl(base.Transformation):
	'''Traverse a term application.'''

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = matching.MatchStr(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = TraverseList(args)
		else:
			self.args = args
				
	def apply(self, term, context):
		try:
			old_name = term.name
			old_args = term.args
		except AttributeError:
			raise exception.Failure
		
		new_name = self.name.apply(old_name, context)
		new_args = self.args.apply(old_args, context)
		
		if new_name is not old_name or new_args is not old_args:
			return term.factory.makeAppl(
				new_name,
				new_args,
				term.annotations
			)
		else:
			return term



def Map(operand):
	map = base.Proxy()
	map.subject = matching.MatchNil() | TraverseCons(operand, map)
	return map


def Fetch(operand):
	fetch = base.Proxy()
	fetch.subject = TraverseCons(operand, combinators.Ident()) | TraverseCons(combinators.Ident(), fetch)
	return fetch


def Filter(operand):
	filter = base.Proxy()
	filter.subject = matching.MatchNil() | FilterCons(operand, filter)
	return filter


class All(combinators.Unary):
	'''Applies a transformation to all subterms of a term.'''
	
	def __init__(self, operand):
		combinators.Unary.__init__(self, operand)
		self.list_transf = Map(operand)
		self.appl_transf = TraverseAppl(combinators.Ident(), self.list_transf)
	
	def apply(self, term, context):
		if term.type == aterm.types.APPL:
			return self.appl_transf.apply(term, context)
		elif term.type == aterm.types.LIST:
			return self.list_transf.apply(term, context)
		else:
			return term


def BottomUp(operand):
	bottomup = base.Proxy()
	bottomup.subject = All(bottomup) & operand
	return bottomup


def TopDown(operand):
	topdown = base.Proxy()
	topdown.subject = operand & All(topdown)
	return topdown


def InnerMost(operand):
	innermost = base.Proxy()
	innermost.subject = BottomUp(combinators.Try(operand & innermost))
	return innermost
