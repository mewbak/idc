"""Simplify Expression"""


from transf import parse
import ir.path


parse.Transfs(r'''

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


testAnd =
	!Binary(And(Int(32,Signed)),Sym("x"),Sym("x")) ;
	OnceTD(simplify) ;
	?Sym("x")

''')
