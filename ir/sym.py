'''Symbol handling transformations.'''


from transf import parse
import ir.match


parse.Transfs('''

#######################################################################
# Local variable table

global localTbl[]

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get('Reg'))
isTmp = combine.Where(annotation.Get('Tmp'))

isLocalVar =
	ir.match.aSym ;
	(isReg + isTmp)

updateLocalVar =
	global localTbl in
		isLocalVar ;
		localTbl.set
	end

updateLocalVars =
	global localTbl in
		localTbl.unset ;
		traverse.AllTD(updateLocalVar)
	end

EnterFunction(operand) =
	updateLocalVars ;
	operand

EnterModule(operand) = EnterFunction(operand)

''')

