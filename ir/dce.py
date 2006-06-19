'''Dead Code Elimination.'''


from transf import *


setLocalVar = build.List((base.ident, base.ident)) & variable.Set('local')
# FIXME: this is machine dependent -- we should search the locally declared vars
setLocalVars = parse.Transf('''
	Where(<Map(setLocalVar)> [
		"eax", "ebx", "ecx", "edx",
		"esi", "edi", "ebp", "esp",
		"ax", "bx", "cx", "dx",
		"si", "di", "bp", "sp",
		"ah", "bh", "ch", "dh",
		"al", "bl", "cl", "dl",
		"nf", "zf", "af", "pf",
		"cf", "of", "df", "if"
	])
''')
setLocalVars = debug.Trace(setLocalVars, 'setLocalVars')

def isTempVar(term, ctx):
	if term.value.startswith('tmp'):
		return term
	raise exception.Failure
isTempVar = match.aStr & util.Adaptor(isTempVar)

clearLocalVars = table.Clear('local')
isVarLocal = isTempVar | table.Get('local')

setUnneededVar = table.Del('needed')
#setUnneededVar = build.List((base.ident,)) & variable.Set('needed')
setNeededVar = table.Set('needed', base.ident)
#setNeededVar = build.List((base.ident,base.ident)) & variable.Set('needed')

setNeededVars = parse.Transf('''
	AllTD(?Sym(<setNeededVar>))
''')

setAllUnneededVars = table.Clear('needed')
def setAllNeededVars(term, ctx):
	local = ctx['local']
	for name in local.terms:
		ctx['needed'].terms[name] = name
	return term
setAllNeededVars = util.Adaptor(setAllNeededVars)

parse.Transfs(r'''

isVarNeeded = ?needed + Not(isVarLocal)
isVarNeeded = debug.Trace(isVarNeeded, `'isVarNeeded'`)

dceStmt = Proxy()
dceStmts = Proxy()

dceAssign = 
	{x:
		?Assign(_, Sym(x), _) ;
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
		setLocalVars; 
		setAllUnneededVars; 
		dceStmts; 
		clearLocalVars
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

