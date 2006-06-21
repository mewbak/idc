'''Transformation combinators.'''


__docformat__ = 'epytext'


from transf import exception
from transf import base
from transf import operate


class _Not(operate.Unary):

	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			self.operand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			raise exception.Failure

def Not(operand):
	'''Fail if a transformation applies.'''
	if operand is base.ident:
		return base.fail
	if operand is base.fail:
		return base.ident
	return _Not(operand)


class _Try(operate.Unary):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	
	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			return self.operand.apply(term, ctx)
		except exception.Failure:
			return term

def Try(operand):
	if operand is base.ident:
		return operand
	if operand is base.fail:
		return base.ident
	return _Try(operand)


class _Where(operate.Unary):

	__slots__ = []
	
	def apply(self, term, ctx):
		self.operand.apply(term, ctx)
		return term

def Where(operand):
	'''Succeeds if the transformation succeeds, but returns the original term.'''
	if operand is base.ident:
		return base.ident
	if operand is base.fail:
		return base.ident
	return _Where(operand)


class _Composition(operate.Binary):

	__slots__ = []
	
	def apply(self, term, ctx):
		term = self.loperand.apply(term, ctx)
		return self.roperand.apply(term, ctx)

def Composition(loperand, roperand):
	'''Transformation composition.'''
	if loperand is base.ident:
		return roperand
	if roperand is base.ident:
		return loperand
	if loperand is base.fail:
		return base.fail
	return _Composition(loperand, roperand)
	

class _Choice(operate.Binary):

	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			return self.loperand.apply(term, ctx)
		except exception.Failure:
			return self.roperand.apply(term, ctx)

def Choice(loperand, roperand):
	'''Attempt the first transformation, transforming the second on failure.'''
	if loperand is base.ident:
		return base.ident
	if loperand is base.fail:
		return roperand
	if roperand is base.ident:
		return Try(loperand)
	if roperand is base.fail:
		return loperand
	return _Choice(loperand, roperand)
	

class _GuardedChoice(operate.Ternary):

	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			term = self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)

def GuardedChoice(operand1, operand2, operand3):
	'''If operand1 succeeds then operand2 is applied, otherwise operand3 is 
	applied. If operand2 fails, the complete expression fails; no backtracking to
	operand3 takes place.
	''' 
	if operand1 is base.ident:
		return operand2
	if operand1 is base.fail:
		return operand3
	if operand2 is base.ident:
		return Choice(operand1, operand3)
	if operand3 is base.fail:
		return Composition(operand1, operand2)
	return _GuardedChoice(operand1, operand2, operand3)


class _IfThen(operate.Binary):

	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			self.loperand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			return self.roperand.apply(term, ctx)

def IfThen(loperand, roperand):
	if loperand is base.ident:
		return roperand
	if loperand is base.fail:
		return base.ident
	if roperand is base.ident:
		return Where(loperand)
	if roperand is base.fail:
		return Not(loperand)
	return _IfThen(loperand, roperand)


class _IfThenElse(operate.Ternary):

	__slots__ = []
	
	def apply(self, term, ctx):
		try:
			self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)

def IfThenElse(operand1, operand2, operand3):
	if operand1 is base.ident:
		return operand2
	if operand1 is base.fail:
		return operand3
	if operand3 is base.fail:
		return IfThen(operand1, operand2)
	return _IfThenElse(operand1, operand2, operand3)


def Switch(cond, cases, otherwise = None):
	'''Sugar around L{IfThenElse}.'''
	
	from transf import context
	from transf import scope
	from transf import match
	from transf import build
	
	if otherwise is None:
		otherwise = base.fail
	
	if cond is not base.ident:		
		tmp_nam = scope.Anonymous('switch')
		match_tmp = match.Var(tmp_nam)
		build_tmp = build.Var(tmp_nam)	
		return scope.Local(
			match_tmp * cond * operate.Nary(
				iter(cases), 
				lambda (case, action), rest: \
					IfThenElse(case, build_tmp * action, rest),
				build_tmp * otherwise
			),
			[tmp_nam]
		)
	else:
		operate.Nary(
			iter(cases), 
			lambda (case, action), rest: \
				IfThenElse(case, action, rest),
			otherwise
		)
