"""Consolidate."""


import refactoring
from refactoring._common import CommonRefactoring


import paths
import transf as lib
from ir.path import *

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

# TODO: liftIfElse

liftLoop =
		with label, rest in
			~[Label(label), *<AtSuffix(
				?[<goto>, *rest] ; 
				![]
			) ; 
			![While(Lit(Bool,1), Block(<id>)), *rest]
			>]
		end

liftWhile =
		with label, cond, rest in
			~[Label(label), *<AtSuffix(
				?[If(_,<goto>,NoStmt), *] ; 
				?[If(cond,_,_), *rest] ; 
				![]
			) ; 
			# XXX: this should be a DoWhile, and not a While
			![While(cond, Block(<id>)), *rest]
			>]
		end

liftAll = AtSuffixR(liftIfThen + liftLoop + liftWhile)

gotoSelected = Where(MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(MatchSelectionTo(?Function))

noInput = ![]

csIfThenApply = OnceTD(AtSuffix(liftIfThen))
csIfThenApplicable = gotoSelected ; csIfThenApply

csLoopApply = OnceTD(AtSuffix(liftLoop))
csLoopApplicable = gotoSelected ; csLoopApply

csWhileApply = OnceTD(AtSuffix(liftWhile))
csWhileApplicable = gotoSelected ; csWhileApply

csAllApply = BottomUp(Repeat(liftAll))
csAllApplicable = id # functionSelected

''')

csIf = CommonRefactoring("Consolidate If-Then", csIfThenApplicable, noInput, csIfThenApply)
csLoop = CommonRefactoring("Consolidate Loop", csLoopApplicable, noInput, csLoopApply)
csWhile = CommonRefactoring("Consolidate While", csWhileApplicable, noInput, csWhileApply)
csAll = CommonRefactoring("Consolidate All", csAllApplicable, noInput, csAllApply)


if __name__ == '__main__':
	refactoring.main(csAll)