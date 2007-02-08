'''Term projecting transformations.'''


import aterm.project

from transf import exception
from transf import transformation
from transf.lib import util


class Head(transformation.Transformation):

	def apply(self, term, ctx):
		try:
			return term.head
		except AttributeError:
			raise exception.Failure("not a list construction term", term)

head = Head()


class Tail(transformation.Transformation):

	def apply(self, term, ctx):
		try:
			return term.tail
		except AttributeError:
			raise exception.Failure("not a list construction term", term)

tail = Tail()


first = head
second = tail * head
third = tail * tail * head
fourth = tail * tail * tail * head


def Nth(n):
	if n > 1:
		nth = Tail()
		for i in range(2, n):
			nth = nth * tail
		nth = nth * head
	elif n < 1:
		raise ValueError
	else: # n = 1
		n = head


def Fetch(operand):
	fetch = util.Proxy()
	fetch.subject = head * operand + tail * fetch
	return fetch


class Name(transformation.Transformation):

	def apply(self, term, ctx):
		try:
			name = term.name
		except AttributeError:
			raise exception.Failure("not an application term", term)
		else:
			return term.factory.makeStr(name)

name = Name()


class Args(transformation.Transformation):

	def apply(self, term, ctx):
		try:
			args = term.args
		except AttributeError:
			raise exception.Failure("not an application term", term)
		else:
			return term.factory.makeList(args)

args = Args()


class Subterms(transformation.Transformation):

	def apply(self, term, ctx):
		return aterm.project.subterms(term)

subterms = Subterms()


class Annos(transformation.Transformation):

	def apply(self, term, ctx):
		return term.getAnnotations()

annos = Annos()

