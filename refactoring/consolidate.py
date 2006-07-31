"""Control structure consolidation."""


import refactoring
from refactoring._common import CommonRefactoring

import transf as lib
import ir.path


lib.parse.Transfs('''


#######################################################################
# Labels

updateNeededLabels = 
Where(
	with label in
		?GoTo(Sym(label)) ;
		![label,label] ==> needed_label
	end
)

#######################################################################
# Statements

dceStmt = Proxy()
dceStmts = Proxy()

dceLabel = 
	Try(
		?Label(<Not(~needed_label)>) ;
		!NoStmt
	)

elimBlock = {
	Block([]) -> NoStmt |
	Block([stmt]) -> stmt
}

dceBlock = 
	~Block(<dceStmts>) ;
	Try(elimBlock)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf = 
	~If(_, <dceStmt>, <dceStmt>) ;
	Try(elimIf)

elimWhile = {
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceWhile = 
	~While(_, <dceStmt>) ;
	Try(elimWhile)

elimDoWhile = {
	DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceDoWhile = 
	~DoWhile(_, <dceStmt>) ;
	Try(elimDoWhile)

dceFunction = 
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		~Function(_, _, _, <dceStmts>)
	end

# If none of the above applies, assume all vars are needed
dceDefault = 
	id

dceStmt.subject = 
	?Label < dceLabel +
	?Block < dceBlock +
	?If < dceIf +
	?While < dceWhile +
	?DoWhile < dceDoWhile +
	?Function < dceFunction + 
	id

dceStmts.subject = 
	MapR(dceStmt) ;
	Filter(Not(?NoStmt))

dceModule = 
	~Module(<dceStmts>)

dce =
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		dceModule
	end


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

liftBreak =
		with label in
			?[<?While + ?DoWhile>, Label(label), *] ;
			~[<
				~While(_,<OnceTD(goto; !Break)>) +
				~While(_,<OnceTD(goto; !Break)>)
			>, *]
		end

liftContinue =
		with label in
			~[Label(label), <
				~While(_,<OnceTD(goto; !Continue)>) +
				~DoWhile(_,<OnceTD(goto; !Continue)>)
			>, *]
		end

doReturn =
	with label, rest in
		Where(
			ir.path.projectSelection ;
			?GoTo(Sym(label))
		) ;
		debug.Dump() ;
		OnceTD(
			AtSuffix(
				Where(
					~[Label(label), *<AtSuffix(~[?Ret, *<![]>])>] ; 
					debug.Dump() ;
					Filter(Not(?Label)) ;
					Map(?Assign + ?Ret) ;
					? rest
				)
			)
		) ;
		OnceTD(goto; !Block(rest))
	end
	

liftAll = AtSuffixR(
	liftIfThen + 
	liftIfElse + 
	liftLoop + 
	liftDoWhile +
	liftBreak +
	liftContinue
)

gotoSelected = Where(ir.path.MatchSelectionTo(?GoTo(Sym(_))))
functionSelected = Where(ir.path.MatchSelectionTo(?Function))

noInput = ![]

csIfThenApply = OnceTD(AtSuffix(liftIfThen))
csIfThenApplicable = gotoSelected ; csIfThenApply
csIfThenApply = csIfThenApply; dce

csIfElseApply = OnceTD(AtSuffix(liftIfElse))
csIfElseApplicable = gotoSelected ; csIfElseApply
csIfElseApply = csIfElseApply; dce

csLoopApply = OnceTD(AtSuffix(liftLoop))
csLoopApplicable = gotoSelected ; csLoopApply
csLoopApply = csLoopApply; dce

csDoWhileApply = OnceTD(AtSuffix(liftDoWhile)) 
csDoWhileApplicable = gotoSelected ; csDoWhileApply
csDoWhileApply = csDoWhileApply; dce

csContinueApply = OnceTD(AtSuffix(liftContinue))
csContinueApplicable = gotoSelected ; csContinueApply
csContinueApply = csContinueApply; dce

csReturnApply = doReturn
csReturnApplicable = gotoSelected ; csReturnApply
csReturnApply = csReturnApply; dce

csAllApply = BottomUp(Repeat(liftAll))
csAllApplicable = id # functionSelected

''')

csIfThen = CommonRefactoring("Structure If-Then", csIfThenApplicable, noInput, csIfThenApply)
csIfElse = CommonRefactoring("Structure If-Else", csIfElseApplicable, noInput, csIfElseApply)
csLoop = CommonRefactoring("Structure Loop", csLoopApplicable, noInput, csLoopApply)
csDoWhile = CommonRefactoring("Structure Do-While", csDoWhileApplicable, noInput, csDoWhileApply)
csContinue = CommonRefactoring("Structure Continue", csContinueApplicable, noInput, csContinueApply)
csReturn = CommonRefactoring("Structure Return", csReturnApplicable, noInput, csReturnApply)
#csAll = CommonRefactoring("Structure All", csAllApplicable, noInput, csAllApply)


if __name__ == '__main__':
	refactoring.main(csAll)