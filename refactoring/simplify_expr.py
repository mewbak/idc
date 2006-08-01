"""Expression simplification."""


import refactoring
from refactoring._common import CommonRefactoring
import transf as lib
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

simplifyExpr = CommonRefactoring(
	"Simplify Expression", 
	applicable, input, apply
)


class TestCase(refactoring.TestCase):

	refactoring = simplifyExpr
		
	applyTestCases = [
		('Sym("a")', '["a", "b"]', 'Sym("b")'),
		('Sym("c")', '["a", "b"]', 'Sym("c")'),
		('[Sym("a"),Sym("c")]', '["a", "b"]', '[Sym("b"),Sym("c")]'),
		('C(Sym("a"),Sym("c"))', '["a", "b"]', 'C(Sym("b"),Sym("c"))'),
	]


if __name__ == '__main__':
	refactoring.main(Rename)