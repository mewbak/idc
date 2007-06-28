'''Term traversal transformations.'''


from transf import exception
from transf import transformation
from transf.lib import base
from transf import util
from transf.lib import combine
from transf.lib import iterate
from transf.lib import congruent
from transf.lib import lists


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
	return iterate.Rec(lambda self: operand + All(self))


def AllBU(operand):
	return iterate.Rec(lambda self: All(self) + operand)


def OnceTD(operand, stop = None):
	'''Performs a left to right depth first search/transformation that
	stops as soon as the the transformation has been successfuly applied.
	'''
	if stop is None:
		return iterate.Rec(lambda self: operand + One(self))
	else:
		return iterate.Rec(lambda self: operand + -stop * One(self))


def OnceBU(operand):
	return iterate.Rec(lambda self: One(self) + operand)


def SomeTD(operand):
	return iterate.Rec(lambda self: operand + Some(self))


def SomeBU(operand):
	return iterate.Rec(lambda self: Some(self) + operand)


def ManyTD(operand):
	return iterate.Rec(lambda self: combine.GuardedChoice(operand, All(combine.Try(self)), Some(self)))


def ManyBU(operand):
	return iterate.Rec(lambda self: combine.GuardedChoice(Some(self), combine.Try(operand), operand))


def Leaves(operand, isLeaf):
	return iterate.Rec(lambda self: combine.GuardedChoice(isLeaf, operand, All(self)))
