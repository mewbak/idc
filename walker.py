'''Base classes for term walker construction.

A term walker is a class aimed to process/transform a term as it traverses the
term. It is an extension of the Visitor design pattern.

An aterm walker's interface is very liberal: is up to the caller determine which
method to call and which arguments to pass, and the return value is not
necessarily a term.

As a walker may change its context as it traverses the tree, sucessive calls to
the same walker methods do not necessarily yield the same results.
'''


import sys

import aterm


def _getIntHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Int'), (term.value,)
		
def _getRealHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Real'), (term.value,)

def _getStrHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Str'), (term.value,)

def _getLitHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Lit'), (term.value,)

def _getNilHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Nil'), ()

def _getConsHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Cons'), (term.head, term.tail)

def _getListHandler(walker, term, prefix):
	return getattr(walker, prefix + 'List'), (term,)

def _getApplHandler(walker, term, prefix):
	try:
		return getattr(walker, prefix + 'Appl' + term.name.value), tuple(term.args)
	except AttributeError:
		return getattr(walker, prefix + 'Appl'), (term.name, term.args)

def _getTermHandler(walker, term, prefix):
	return getattr(walker, prefix + 'Term'), (term,)

_getHandlersTable = {
	aterm.types.INT: (_getIntHandler, _getLitHandler, _getTermHandler),
	aterm.types.REAL: (_getRealHandler, _getLitHandler, _getTermHandler),
	aterm.types.STR: (_getStrHandler, _getLitHandler, _getTermHandler),
	aterm.types.NIL: (_getNilHandler, _getListHandler, _getTermHandler),
	aterm.types.CONS: (_getConsHandler, _getListHandler, _getTermHandler),
	aterm.types.APPL: (_getApplHandler, _getTermHandler),
}

def _getHandler(walker, term, prefix):
	try:
		hgs = _getHandlersTable[term.type]
	except KeyError:
		hgs = (_getTermHandler,)
	
	for hg in hgs:
		try:
			return hg(walker, term, prefix)
		except AttributeError:
			pass
	raise AttributeError
	

class Walker(object):
	'''Base class for term walkers.'''

	def __init__(self):
		pass

	# TODO: handle annotations?
	# TODO: pass the term arg?
	
	def _dispatch(self, term, prefix, **kargs):
		'''Dispatch the term to a method with a name starting with the given 
		prefix, and a suffix determined from the term.
		
		Suffixes are (listed by the order their are tried):
		- Int for an integer term
		- Real for an integer term
		- Str for a string term
		- Lit for a generic literal term
		- Nil for a nil list term
		- Cons for a cons list term
		- List for a generic list term
		- ApplName for an Name application term
		- Appl for a generic application term
		- Term for a generic term
		'''
		
		try:
			method, args = _getHandler(self, term, prefix)
		except AttributeError:
			raise ValueError("unexpected term", term)
		else:
			return method(*args, **kargs)

	def _int(self, term):
		'''Get the value of an integer term.'''
		if term.type != aterm.types.INT:
			raise TypeError("not an integer term", term)
		return term.value
	
	def _real(self, term):
		'''Get the value of a real term.'''
		if term.type != aterm.types.REAL:
			raise TypeError("not a real term", term)
		return term.value
	
	def _str(self, term):
		'''Get the value of a string term.'''
		if term.type != aterm.types.STR:
			raise TypeError("not a string term", term)
		return term.value
	
	def _lit(self, term):
		'''Get the value of a literal term.'''
		if not term.type in (aterm.types.INT, aterm.types.REAL, aterm.types.STR):
			raise TypeError("not a literal term", term)
		return term.value
	
	def _obj(self, term):
		'''Convert the term to a python object.'''
		return self._dispatch(term, '_obj')

	def _objLit(self, value):
		return value
	
	def _objList(self, terms):
		return map(self._obj, terms)

	# XXX: is this actually useful?
	def _match(self, term, pattern):
		'''Match the term against the given pattern. Variables are stored in 
		the caller's local namespace.
		'''
		match = term.rmatch(pattern)
		if match:
			caller = sys._getframe(1)
			caller.f_locals.update(match.kargs)
			return True
		else:
			return False

	# TODO: implement methods for collecting terms?
	
