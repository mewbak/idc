'''Sugaring transformations.'''
	

from transf import context
from transf import base
from transf import combine
from transf import scope
from transf import build
from transf import match


def _Iter(iter, Cons, tail):
	try:
		head = iter.next()
	except StopIteration:
		return tail
	else:
		rest = _Iter(iter, Cons, tail)
		return Cons(head, rest)


def Switch(cond, cases, otherwise = None):
	if otherwise is None:
		otherwise = base.fail
	
	if cond is not base.ident:		
		tmp_nam = context.Anonymous('switch')
		match_tmp = match.Var(tmp_nam)
		build_tmp = build.Var(tmp_nam)	
		return scope.Local(
			match_tmp & cond & _Iter(
				iter(cases), 
				lambda (case, action), rest: \
					combine.IfThenElse(case, build_tmp & action, rest),
				build_tmp & otherwise
			),
			[tmp_nam]
		)
	else:
		_Iter(
			iter(cases), 
			lambda (case, action), rest: \
				combine.IfThenElse(case, action, rest),
			otherwise
		)
