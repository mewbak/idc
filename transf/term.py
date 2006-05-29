'''Transformations for term (de)construction.'''

import aterm.types
import aterm.visitor

from transf.base import *


class _Lit(Transformation):

	def __init__(self, type, value):
		Transformation.__init__(self)
		self.type = type
		self.value = value

	def __call__(self, term):
		if term.type != self.type or term.value != self.value:
			raise Failure
		return term


def Int(value):
	return _Lit(aterm.types.INT, value)
	

def Real(value):
	return _Lit(aterm.types.REAL, value)


def Str(value):
	return _Lit(aterm.types.STR, value)
	

class Nil(Transformation):

	def __call__(self, term):
		if term.type != aterm.types.LIST or not term.isEmpty():
			raise Failure
		return term


class Cons(Transformation):
	
	def __init__(self, head, tail):
		self.head_transf = head
		self.tail_transf = tail
		
	def __call__(self, term):
		if term.type != aterm.types.LIST or term.isEmpty():
			raise Failure
		old_head = term.head
		old_tail = term.tail
		new_head = self.head_transf(old_head)
		new_tail = self.tail_transf(old_tail)
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


def _List(args_iter, tail):
	try:
		arg = args_iter.next()
	except StopIteration:
		return tail
	else:
		return Cons(arg, _List(args_iter, tail))


def List(args, tail = None):
	if tail is None:
		transf = Nil()
	else:
		transf = tail
	return _List(iter(args), tail)
	

class Appl(Transformation):

	def __init__(self, name, args):
		if isinstance(name, basestring):
			self.name_transf = Str(name)
		else:
			self.name_transf = name
		self.args_transf = args
		
	def __call__(self, term):
		if term.type != aterm.types.APPL:
			raise Failure
		
		old_name = term.name
		old_args = term.args
		new_name = self.name_transf(old_name)
		new_args = self.args_transf(old_args)
		
		if new_name is not old_name or new_args is not old_args:
			return term.factory.makeAppl(
				new_name,
				new_args,
				term.annotations
			)
		else:
			return term
		

	