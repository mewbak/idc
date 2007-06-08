'''Symbol handling transformations.'''


from transf import parse
import ir.match


parse.Transfs('''

#######################################################################
# Local variable table

shared localTbl as table

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get(`"Reg"`))
isTmp = combine.Where(annotation.Get(`"Tmp"`))

isLocalVar =
	ir.match.aSym ;
	(isReg + isTmp)

updateLocalVar =
	isLocalVar ;
	localTbl.set [_,_]

updateLocalVars =
	localTbl.clear ;
	traverse.AllTD(updateLocalVar)

EnterFunction(operand) =
	with localTbl in
		updateLocalVars ;
		operand
	end

EnterModule(operand) = EnterFunction(operand)

''')

