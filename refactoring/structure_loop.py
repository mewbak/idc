"""Refactoring Loop."""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import lib
import ir.path


lib.parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))


liftLoop =
		with label, rest in
			~[Label(label), *<AtSuffix(
				?[<goto>, *rest] ;
				![]
			) ;
			![While(Lit(Bool,1), Block(<id>)), *rest]
			>]
		end


gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = OnceTD(AtSuffix(liftLoop))
applicable = gotoSelected ; apply
apply = apply; dle


''')
