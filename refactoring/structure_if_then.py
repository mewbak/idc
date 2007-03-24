"""Structure If-Then."""


import refactoring
from refactoring.dead_label_elimination import dce

from transf import lib
import ir.path


lib.parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftIfThen =
		with cond, label, rest in
			~[If(cond, <goto>, NoStmt), *<AtSuffix(
				?[Label(label), *] ; ?rest ;
				![]
			)>] ;
			![If(Unary(Not(Bool), cond), Block(<project.tail>), NoStmt), *rest]
		end

gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = OnceTD(AtSuffix(liftIfThen))
applicable = gotoSelected ; apply
apply = apply; dce


''')
