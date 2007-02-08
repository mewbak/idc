"""Add function argument."""


import refactoring
from refactoring._common import CommonRefactoring

from transf import lib
import ir.traverse
import ir.path


lib.parse.Transfs('''

applicable =
	ir.path.projectSelection ; ?Function(_, _, _, _)

input =
	with name, arg in
		ir.path.projectSelection ; ?Function(_, ?name, _, _) ;
		lib.input.Str(!"Add Function Argument", !"Argument Symbol?") ; ?arg ;
		![name, arg]
	end

apply =
	with name, type, arg in
		Where(!args; ?[name, arg]) ;
		Where(!Int(32,Signed); ?type) ;
		~Module(<
			One(
				~Function(_, ?name, <Concat(id,![Arg(type,arg)])>, _)
			)
		>) ;
		BottomUp(Try(
			~Call(Sym(?name), <Concat(id,![Sym(arg)])>)
		))
	end
''')

addFunctionArg = CommonRefactoring(
	"Add Function Argument",
	applicable, input, apply
)


if __name__ == '__main__':
	refactoring.main(addFunctionArg)
