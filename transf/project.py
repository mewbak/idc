'''Term projecting transformations.'''


import aterm.types

from transf import exception
from transf import base


class Head(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.head
		except AttributeError:
			raise exception.Failure("not a list construction term", term)

head = Head()


class Tail(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.tail
		except AttributeError:
			raise exception.Failure("not a list construction term", term)

tail = Tail()


first = head
second = tail & head
third = tail & tail & head
fourth = tail & tail & tail & head


def Nth(n):
	if n > 1:
		nth = Tail()
		for i in range(2, n):
			nth = nth & tail
		nth = nth & head
	elif n < 1:
		raise ValueError
	else: # n = 1
		n = head


class Name(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.name
		except AttributeError:
			raise exception.Failure("not an application term", term)

name = Name()


class Args(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.args
		except AttributeError:
			raise exception.Failure("not an application term", term)

args = Args()


class SubTerms(base.Transformation):
	
	def apply(self, term, context):
		if term.type == aterm.types.APPL:
			return term.args
		if term.type == aterm.types.LIST:
			return term
		return term.factory.makeNil()

subterms = SubTerms()

