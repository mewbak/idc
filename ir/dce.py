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
		"NF", "ZF", "AF", "PF",
		"CF", "OF", "DF", "IF",
		"FP", "SKIP", "RPT", "FLF",
		"C1", "C2", "FZF"
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

dceAssign = parse.Transf('''
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
''')

dceAsm = parse.Transf('''
	?Asm(*) ;
	setAllNeededVars
''')

dceLabel = parse.Transf('''
	?Label(*)
''')

dceBranch = parse.Transf('''
	?Branch(*) ;
	setAllNeededVars
''')

dceRet = parse.Transf('''
	?Ret(*) ;
	setAllUnneededVars ;
	debug.Dump(); ~Ret(_, <setNeededVars>) ;
	debug.Dump()
''')

elimIf = parse.Rule('''
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
''')

dceIf = parse.Transf('''
	?If(*) ;
	JoinNeededVars(
		~If(_, <dceStmt>, _),
		~If(_, _, <dceStmt>)
	) ;
	try(elimIf) ;
	~If(<setNeededVars>, _, _)
''')

elimBlock = parse.Rule('''
	Block([]) -> NoStmt
''')

dceBlock = parse.Transf('''
	~Block(<dceStmts>) ;
	try(elimBlock)
''')

dceFuncDef = parse.Transf('''
	~FuncDef(_, _, _, <
		setLocalVars; 
		setAllUnneededVars; 
		dceStmt; 
		clearLocalVars
	>)
''')

dceStmt.subject = parse.Transf('''
	dceAssign +
	dceAsm +
	dceLabel +
	dceBranch +
	dceRet +
	dceBlock +
	dceIf +
	dceFuncDef
''')

dceStmts.subject = parse.Transf('''
	filterr(try(dceStmt) ; not(?NoStmt))
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
