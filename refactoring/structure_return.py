"""Structure Return"""


import refactoring
from refactoring.dead_label_elimination import dce

from transf import lib
import ir.path


lib.parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

doReturn =
	with label, rest in
		Where(
			ir.path.projectSelection ;
			?GoTo(Sym(label))
		) ;
		OnceTD(
			AtSuffix(
				Where(
					~[Label(label), *<AtSuffix(~[?Ret, *<![]>])>] ;
					Filter(Not(?Label)) ;
					Map(?Assign + ?Ret) ;
					? rest
				)
			)
		) ;
		OnceTD(goto; !Block(rest))
	end


gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = doReturn; dce
applicable = gotoSelected ; doReturn

''')
