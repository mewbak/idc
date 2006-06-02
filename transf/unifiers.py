'''Term unifying transformations.'''


import aterm

from transf import base
from transf import combinators
from transf import matching
from transf import building
from transf import projection


def Foldr(tail, cons, operand=None):
	if operand is None:
		operand = combinators.Ident()
	foldr = base.Proxy()
	foldr.subject \
		= matching.MatchNil() & tail \
		| building.BuildList((
			projection.Head() & operand, 
			projection.Tail() & foldr
		)) & cons
	return foldr



