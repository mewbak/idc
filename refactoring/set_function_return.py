"""Set function return."""


"""Consolidate Control Structures."""


import refactoring
from refactoring._common import CommonRefactoring

import transf as lib
import ir.traverse
import ir.path


lib.parse.Transfs('''

applicable =
	ir.path.projectSelection ; ?Function(Void, _, _, _)

input = 
	with name, ret in
		ir.path.projectSelection ; ?Function(_, name, _, _) ;
		lib.input.Str(!"Set Function Return", !"Return Symbol?") ; ?ret ;
		![name, ret]
	end 

apply = 
	with name, type, ret in
		Where(!args; ?[name, ret]) ;
		Where(!Int(32,Signed); ?type) ;
		~Module(<
			One(
				~Function(!type, ?name, _, <
					AllTD(~Ret(!type, !Sym(ret)))
				>) 
			)
		>) ;
		ir.traverse.AllStmtsBU(Try(
			?Assign(Void, NoExpr, Call(Sym(?name), _)) ;
			~Assign(!type, !Sym(ret), _)
		))
	end
''')

setFunctionReturn = CommonRefactoring(
	"Set Function Return", 
	applicable, input, apply
)


if __name__ == '__main__':
	refactoring.main(setFunctionReturn)
