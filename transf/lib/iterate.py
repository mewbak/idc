'''Transformations for iterating terms.'''


from transf.lib import util
from transf.lib import combine


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = util.Proxy()
	repeat.subject = +(operand * repeat)
	return repeat


def Rec(Def):
	'''Recursive transformation.

	@param Def: transformation factory whose single argument is its own definition.
	'''
	rec = util.Proxy()
	rec.subject = Def(rec)
	return rec