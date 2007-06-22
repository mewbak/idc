'''Type verification.'''


from aterm import types


# TODO: merge into the types module


def anInt(term):
	'''Integer term type verifier.'''
	return term.type == types.INT


def aReal(term):
	'''Real term type verifier.'''
	return term.type == types.REAL


def aStr(term):
	'''String term type verifier.'''
	return term.type == types.STR


def aLit(term):
	'''Literal term type verifier.'''
	return term.type & types.LIT


def aNil(term):
	'''Empty list term type verifier.'''
	return term.type == types.NIL


def aCons(term):
	'''List construction term type verifier.'''
	return term.type == types.CONS


def aList(term):
	'''List term type verifier.'''
	return term.type & types.LIST


def anAppl(term):
	'''Application term type verifier.'''
	return term.type == types.APPL
