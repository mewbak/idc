'''Dead Code Elimination.'''


from transf import *
import ir.match


#######################################################################
# Local var table

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get('Reg'))
isTmp = combine.Where(annotation.Get('Tmp'))
isLocalVar = ir.match.aSym * (isReg + isTmp)

markLocalVar = isLocalVar * table.Set('locals') * debug.Log('Found local %s\n', base.ident)
markLocalVars = traverse.AllTD(markLocalVar)

def EnterLocals(operand):
	return scope.With((
			('locals', table.new),
		),
		markLocalVars * operand
	)


#######################################################################
# Needed/uneeded table

setUnneededVar = table.Del('needed')
setNeededVar = table.Set('needed', base.ident)

setNeededVars = traverse.AllTD(ir.match.aSym * setNeededVar)

setAllUnneededVars = table.Clear('needed')
setAllNeededVars = table.Add('needed', 'local')

parse.Transfs(r'''

isVarNeeded = ir.match.aSym ; (?needed + Not(isLocalVar))
isVarNeeded = debug.Trace(isVarNeeded, `'isVarNeeded'`)

dceStmt = Proxy()
dceStmts = Proxy()

dceAssign = 
	{x:
		?Assign(_, x, _) ;
		if <isVarNeeded> x then
			<setUnneededVar> x ;
			~Assign(_, _, <setNeededVars>)
		else
			!NoStmt
		end
	} +
	~Assign(_, <setNeededVars>, <setNeededVars>)

dceAsm = 
	?Asm ;
	setAllNeededVars

dceLabel = 
	?Label

dceJump = 
	?Jump ;
	setAllNeededVars

dceRet = 
	?Ret ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf = 
	?If ;
	~If(_, <dceStmt>, _) \needed/ ~If(_, _, <dceStmt>) ;
	Try(elimIf) ;
	~If(<setNeededVars>, _, _)

elimBlock = {
	Block([]) -> NoStmt
}

dceBlock = 
	~Block(<dceStmts>) ;
	Try(elimBlock)

dceFunc = 
	~Func(_, _, _, <
		EnterLocals(
			setAllUnneededVars; 
			dceStmts
		)
	>)

# If none of the above applies, assume all vars are needed
dceDefault = 
	setAllNeededVars

dceStmt.subject = 
	dceAssign +
	dceAsm +
	dceLabel +
	dceJump +
	dceRet +
	dceBlock +
	dceIf +
	dceFunc + 
	dceDefault

dceStmts.subject = 
	FilterR(
		Try(dceStmt) ; 
		Not(?NoStmt)
	)

dceModule = 
	~Module(<dceStmts>)

dce =
	with needed[], local[] in
		dceModule
	end
''')

