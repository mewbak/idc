'''Helper transformation factory for short-cutting code.'''


import aterm.term
from transf import transformation
from transf.lib import base


class Factory(object):

	def __init__(self, Int, Real, Str, List, Appl, Var, Term):
		self.__Int = Int
		self.__Real = Real
		self.__Str = Str
		self.__List = List
		self.__Appl = Appl
		self.__Var = Var
		self.__Term = Term

	def __coerce(self, arg):
		if isinstance(arg, transformation.Transformation):
			return arg
		if isinstance(arg, int):
			return self.__Int(arg)
		if isinstance(arg, float):
			return self.__Real(arg)
		if isinstance(arg, basestring):
			return self.__Str(arg)
		if isinstance(arg, (tuple, list)):
			return self.__List(map(self.__coerce, arg))
		if isinstance(arg, aterm.term.Term):
			self.__Term(arg)
		raise TypeError, 'cannot coerce arg %r' % arg

	def __getattribute__(self, name):
		inicial = name[0]
		if inicial == '_':
			if name == '_':
				return base.ident
			else:
				return object.__getattribute__(self, name)
		if inicial.isupper():
			return lambda *args: self.__Appl(name, map(self.__coerce, args))
		if inicial.islower():
			return self.__Var(name)
		raise AttributeError

	def __getitem__(self, key):
		if isinstance(key, tuple):
			return self.__List(map(self.__coerce, key))
		else:
			return self.__List([self.__coerce(key)])

	def __apply__(self, *args):
		return self.__List(map(self.__coerce, args))

