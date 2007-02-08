'''Symbol handling transformations.'''


from transf import types
from transf.lib import *
import ir.match


#######################################################################
# Local variable table

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get('Reg'))
isTmp = combine.Where(annotation.Get('Tmp'))
isLocalVar = ir.match.aSym * (isReg + isTmp)

updateLocalVar = (
	isLocalVar *
	types.table.Set('local')
)

updateLocalVars = traverse.AllTD(updateLocalVar)

parse.Transfs('''
EnterFunction(operand) =
	with local[] in
		updateLocalVars ;
		operand
	end
''')

EnterModule = EnterFunction
