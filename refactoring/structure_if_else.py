"""Structure If-Else"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftIfElse =
		with
			cond, false_stmts,
			true_label, true_stmts,
			rest_label, rest_stmts
		in
			~[If(cond, <ir.path.inSelection;?GoTo(Sym(true_label))>, NoStmt), *<AtSuffix(
				~[GoTo(Sym(rest_label)), Label(true_label), *<AtSuffix(
					?[Label(rest_label), *] => rest_stmts ;
					![]
				)>] ; project.tail => true_stmts ;
				![]
			)>] ; project.tail => false_stmts ;
			![If(cond, Block(true_stmts), Block(false_stmts)), *rest_stmts]
		end

gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = OnceTD(AtSuffix(liftIfElse))
applicable = gotoSelected ; apply
apply = apply; dle

''')
