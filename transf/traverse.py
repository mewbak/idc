'''Term traversal transformations.'''


from transf import exception
from transf import base
from transf import util
from transf import congruent
from transf import lists


def All(operand):
	'''Applies a transformation to all direct subterms of a term.'''
	return congruent.Subterms(lists.Map(operand), base.ident)


def One(operand):
	'''Applies a transformation to exactly one direct subterm of a term.'''
	one = util.Proxy()
	one.subject = congruent.Subterms(
		congruent.Cons(operand, base.ident) + congruent.Cons(base.ident, one), 
		base.fail
	)
	return one


def Some(operand):
	'''Applies a transformation to as many direct subterms of a term, but at list one.'''
	some = util.Proxy()
	some.subject = congruent.Subterms(
		congruent.Cons(operand, lists.Map(+operand)) + congruent.Cons(base.ident, some),
		base.fail
	)
	return some


def Traverse(Subterms, down = None, up = None, stop = None, Enter = None, Leave = None):
	'''Generic traversal.'''
	traverse = util.Proxy()
	traverse.subject = Subterms(traverse)
	if Leave is not None:
		traverse.subject = Leave(traverse.subject)
	if stop is not None:
		traverse.subject = stop + traverse.subject
	if up is not None:
		traverse.subject = traverse.subject * up
	if down is not None:
		traverse.subject = down * traverse.subject
	if Enter is not None:
		traverse.subject = Enter(traverse.subject)
	return traverse


def DownUp(down = None, up = None, stop = None):
	downup = util.Proxy()
	downup.subject = All(downup)
	if stop is not None:
		downup.subject = stop + downup.subject
	if up is not None:
		downup.subject = downup.subject * up
	if down is not None:
		downup.subject = down * downup.subject
	return downup


def TopDown(operand, stop = None):
	return DownUp(down = operand, stop = stop)


def BottomUp(operand, stop = None):
	return DownUp(up = operand, stop = stop)


def InnerMost(operand):
	innermost = util.Proxy()
	innermost.subject = BottomUp(+(operand * innermost))
	return innermost


def AllTD(operand):
	'''Apply a transformation to all subterms, but stops recursing 
	as soon as it finds a subterm to which the transformation succeeds.
	'''
	alltd = util.Proxy()
	alltd.subject = operand + All(alltd)
	return alltd
