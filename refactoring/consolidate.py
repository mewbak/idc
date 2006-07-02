"""Control structure consolidation."""


import refactoring
from refactoring._common import CommonRefactoring

import transf as lib
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

gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

noInput = ![]

csIfThenApply = OnceTD(AtSuffix(liftIfThen))
csIfThenApplicable = gotoSelected ; csIfThenApply

csIfElseApply = OnceTD(AtSuffix(liftIfElse))
csIfElseApplicable = gotoSelected ; csIfElseApply

csLoopApply = OnceTD(AtSuffix(liftLoop))
csLoopApplicable = gotoSelected ; csLoopApply

csWhileApply = OnceTD(AtSuffix(liftWhile))
csWhileApplicable = gotoSelected ; csWhileApply

csAllApply = BottomUp(Repeat(liftAll))
csAllApplicable = id # functionSelected

''')

csIfThen = CommonRefactoring("Consolidate If-Then", csIfThenApplicable, noInput, csIfThenApply)
csIfElse = CommonRefactoring("Consolidate If-Else", csIfElseApplicable, noInput, csIfElseApply)
csLoop = CommonRefactoring("Consolidate Loop", csLoopApplicable, noInput, csLoopApply)
csWhile = CommonRefactoring("Consolidate While", csWhileApplicable, noInput, csWhileApply)
csAll = CommonRefactoring("Consolidate All", csAllApplicable, noInput, csAllApply)


if __name__ == '__main__':
	refactoring.main(csAll)