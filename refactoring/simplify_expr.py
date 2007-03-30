"""Simplify Expression"""


from transf import lib
import ir.path


lib.parse.Transfs(r'''

simplify = {
	Binary(Eq(Int(_,_)),Binary(Minus(Int(_,_)),x,y),Lit(Int(_,_),0))
		-> Binary(Eq(t),x,y) |
	Unary(Not(Bool),Binary(Eq(t),x,y))
		-> Binary(NotEq(t),x,y) |
	Binary(And(_),x,x)
		-> x
}

applicable =
	ir.path.projectSelection ;
	ir.match.expr ;
	OnceTD(simplify)

input = ![]

apply =
	OnceTD(
		ir.path.isSelected ;
		InnerMost(simplify)
	)

''')


applyTestCases = [
	('Binary(And(Int(32,Signed)),Sym("x"),Sym("x"))', '[[]]', 'Sym("x")'),
]
