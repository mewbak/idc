"""Structure While"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import lib
import ir.path


lib.parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftDoWhile =
		with label, cond, rest in
			~[Label(label), *<AtSuffix(
				?[If(_,<goto>,NoStmt), *] ;
				?[If(cond,_,_), *rest] ;
				![]
			) ;
			![DoWhile(cond, Block(<id>)), *rest]
			>]
		end

gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = OnceTD(AtSuffix(liftDoWhile))
applicable = gotoSelected ; apply
apply = apply; dle

testApply =
	!Module([
		Label("next"),
		Assign(Int(32,Signed), Sym("a"), Sym("b")),
		If(Sym("a"),GoTo(Sym("next")),NoStmt)
	]) ;
	ir.path.annotate ;
	with selection = ![1,2,0] in apply end ;
	debug.Dump() ;
	?Module([
		DoWhile(Sym("a"),
			Assign(Int(32,Signed), Sym("a"), Sym("b"))
		)
	])
''')
