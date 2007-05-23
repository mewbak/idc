'''Symbol handling transformations.'''


from transf import types
from transf import parse
import ir.match


parse.Transfs('''

#######################################################################
# Local variable table

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get('Reg'))
isTmp = combine.Where(annotation.Get('Tmp'))

isLocalVar =
	ir.match.aSym ;
	(isReg + isTmp)

updateLocalVar =
	isLocalVar ;
	types.table.Set('local')

updateLocalVars =
	traverse.AllTD(updateLocalVar)

EnterFunction(operand) =
	with local[] in
		updateLocalVars ;
		operand
	end

EnterModule(operand) = EnterFunction(operand)

''')

