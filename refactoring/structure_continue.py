"""Structure Continue"""


import refactoring
from refactoring.dead_label_elimination import dce

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
apply = apply; dce

''')
