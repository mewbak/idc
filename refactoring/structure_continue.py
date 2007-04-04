"""Structure Continue"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import lib
import ir.path


lib.parse.Transfs('''


goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftContinue =
	with label in
		~[Label(label), <
			~While(_,<OnceTD(goto; !Continue)>) +
			~DoWhile(_,<OnceTD(goto; !Continue)>)
		>, *]
	end


gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

input = ![]

apply = OnceTD(AtSuffix(liftContinue))
applicable = gotoSelected ; apply
apply = apply; dle


xtestApply =
	!Module([
		Label("continue"),
		While(Lit(Bool,1), Block([
			Assign(Int(32,Signed), Sym("a"), Sym("b")),
			GoTo(Sym("continue"))
		]))
	]) ;
	ir.path.annotate ;
	debug.Dump() ;
	# 2,0,1,0,0
	with selection = ![0,1,1,0,1] in apply end ;
	debug.Dump() ;
	?Module([
		While(Lit(Bool,1), Block([
			Assign(Int(32,Signed), Sym("a"), Sym("b")),
			Continue
		]))
	])

''')
