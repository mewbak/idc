'''Transformations for term projection.'''


from transf import exception
from transf import base


# TODO: use singletons to speed up instanciation


class Head(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.head
		except AttributeError:
			raise exception.Failure("not a list construction term", term)


class Tail(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.tail
		except AttributeError:
			raise exception.Failure("not a list construction term", term)


def First():
	return Head()


def Second():
	return Tail() & Head()


def Third():
	return Tail() & Tail() & Head()


def Fourth():
	return Tail() & Tail() & Tail() & Head()


def Nth(n):
	if n > 1:
		nth = Tail()
		for i in range(2, n):
			nth = nth & Tail()
		nth = nth & Head()
	elif n < 1:
		raise ValueError
	else: # n = 1
		n = Head()


class Name(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.name
		except AttributeError:
			raise exception.Failure("not an application term", term)


class Args(base.Transformation):
	
	def apply(self, term, context):
		try:
			return term.args
		except AttributeError:
			raise exception.Failure("not an application term", term)

