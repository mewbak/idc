'''Arithmetic transformations.'''


import aterm

from transf import exception
from transf import combine
from transf import project


# TODO: complete


class _Unary(combine.Unary):

	def __init__(self, operand, func):
		combine.Binary.__init__(self, operand)
		self.func = func
		
	def apply(self, term, context):
		x = self.loperand.apply(term, context)
		try:
			return self.func(term,x)
		except TypeError:
			raise exception.Failure('wrong term type', x)


class _Binary(combine.Binary):

	def __init__(self, loperand, roperand, func):
		combine.Binary.__init__(self, loperand, roperand)
		self.func = func
		
	def apply(self, term, context):
		x = self.loperand.apply(term, context)
		y = self.roperand.apply(term, context)
		try:
			return self.func(term,x,y)
		except TypeError:
			raise exception.Failure('wrong term type', x, y)



# TODO: use decorators and/or metaclasses to simplify this

_fnIncInt = lambda t, x: t.factory.makeInt(int(x) + 1)
_fnDecInt = lambda t, x: t.factory.makeInt(int(x) - 1)

IncInt = lambda o: _Unary(o, _fnIncInt)
DecInt = lambda o: _Unary(o, _fnDecInt)

_fnAddInt = lambda t, x, y: t.factory.makeInt(int(x) + int(y))
_fnSubInt = lambda t, x, y: t.factory.makeInt(int(x) + int(y))
_fnMulInt = lambda t, x, y: t.factory.makeInt(int(x) * int(y))
_fnDivInt = lambda t, x, y: t.factory.makeInt(int(x) / int(y))

AddInt = lambda l, r: _Binary(l, r, _fnAddInt)
SubInt = lambda l, r: _Binary(l, r, _fnSubInt)
MulInt = lambda l, r: _Binary(l, r, _fnMulInt)
DivInt = lambda l, r: _Binary(l, r, _fnDivInt)

def _fnBool(t, b):
	if b:
		return t
	else:
		raise exception.Failure

_fnEqInt = lambda t, x, y: _fnBool(t, int(x) == int(y))
_fnNeqInt = lambda t, x, y: _fnBool(t, int(x) != int(y))
_fnGtInt = lambda t, x, y: _fnBool(t, int(x) > int(y))
_fnLtInt = lambda t, x, y: _fnBool(t, int(x) > int(y))
_fnGeqInt = lambda t, x, y: _fnBool(t, int(x) >= int(y))
_fnLeqInt = lambda t, x, y: _fnBool(t, int(x) <= int(y))

EqInt = lambda l, r: _Binary(l, r, _fnEqInt)
NeqInt = lambda l, r: _Binary(l, r, _fnNeqInt)
GtInt = lambda l, r: _Binary(l, r, _fnGtInt)
LtInt = lambda l, r: _Binary(l, r, _fnLtInt)
GeqInt = lambda l, r: _Binary(l, r, _fnGeqInt)
LeqInt = lambda l, r: _Binary(l, r, _fnLeqInt)

Inc = IncInt
Dec = DecInt
Add = AddInt
Sub = SubInt
Mul = MulInt
Div = DivInt
Eq = EqInt
Neq = NeqInt
Gt = GtInt
Lt = LtInt
Geq = GeqInt
Leq = LeqInt

add = Add(project.first, project.second)



