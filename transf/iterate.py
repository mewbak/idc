'''Transformations for iterating terms.'''


from transf import util
from transf import combine


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = util.Proxy()
	repeat.subject = combine.Try(operand & repeat)
	return repeat


def Rec(Def):
	'''Recursive transformation.
	
	@param Def: transformation factory whose single argument is its own definition.
	'''
	rec = util.Proxy()
	rec.subject = Def(rec)
	return rec
