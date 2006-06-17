'''Dead Code Elimination.'''


from transf import *


setLocalVar = table.Set('local', base.ident, base.ident)
# FIXME: this is machine dependent -- we should search the locally declared vars
setLocalVars = parse.Transf('''
	where(<map(setLocalVar)> [
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
setLocalVars = debug.Trace('setLocalVars', setLocalVars)

def isTempVar(term, ctx):
	if term.value.startswith('tmp'):
		return term
	raise exception.Failure
isTempVar = match.aStr & base.Adaptor(isTempVar)

clearLocalVars = table.Clear('local')
isVarLocal = isTempVar | table.Get('local', base.ident)

setUnneededVar = table.Del('needed', base.ident)
setNeededVar = table.Set('needed', base.ident, base.ident)

setNeededVars = parse.Transf('''
	alltd(?Sym(<setNeededVar>))
''')

setAllUnneededVars = table.Clear('needed')
def setAllNeededVars(term, ctx):
	local = ctx['local']
	for name in local:
		ctx['needed'][name] = name
	return term
setAllNeededVars = base.Adaptor(setAllNeededVars)


isVarNeeded = table.Get('needed', base.ident) | combine.Not(isVarLocal)
isVarNeeded = debug.Trace('isVarNeeded', isVarNeeded)

JoinNeededVars = lambda l,r: table.Merge(l, r, ['needed'], [])


dceStmt = base.Proxy()
dceStmts = base.Proxy()

parse.Transfs('''
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
	?Asm(*) ;
	setAllNeededVars

dceLabel = 
	?Label(*)

dceBranch = 
	?Branch(*) ;
	setAllNeededVars

dceRet = 
	?Ret(*) ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf = 
	?If(*) ;
	JoinNeededVars(
		~If(_, <dceStmt>, _),
		~If(_, _, <dceStmt>)
	) ;
	try(elimIf) ;
	~If(<setNeededVars>, _, _)

elimBlock = {
	Block([]) -> NoStmt
}

dceBlock = 
	~Block(<dceStmts>) ;
	try(elimBlock)

dceFuncDef = 
	~FuncDef(_, _, _, <
		setLocalVars; 
		setAllUnneededVars; 
		dceStmt; 
		clearLocalVars
	>)

# If none of the above applies, assume all vars are needed
dceDefault = 
	setAllNeededVars
''')

dceStmt.subject = parse.Transf('''
	dceAssign +
	dceAsm +
	dceLabel +
	dceBranch +
	dceRet +
	dceBlock +
	dceIf +
	dceFuncDef + 
	dceDefault
''')

dceStmts.subject = parse.Transf('''
	filterr(
		try(dceStmt) ; 
		not(?NoStmt)
	)
''')

dceModule = parse.Transf('''
	~Module(<dceStmts>)
''')

dce = scope.Local(
	table.New('needed') &
	table.New('local') &
	dceModule,
	['needed', 'local']
)
