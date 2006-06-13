'''Dead Code Elimination.'''


from transf import *


setUnneededVar = table.Del('nv', base.ident)
setNeededVar = table.Set('nv', base.ident, base.ident)
setNeededVars = parse.Transf('''
	alltd(?Sym(<setNeededVar>))
''')
setAllUnneededVars = table.Clear('nv')
isVarNeeded = debug.Dump() & table.Get('nv', base.ident)

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
''') & debug.Dump()

dceLabel = parse.Transf('''
	?Label(*)
''')

dceReturn = parse.Transf('''
	?Ret(*) ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)
	;debug.Dump()
''')

dceBlock = parse.Transf('''
	~Block(<dceStmts>)
''')

dceFuncDef = parse.Transf('''
	?FuncDef(*) ;
	setAllUnneededVars ;
	~FuncDef(_, _, _, <dceStmt>)
''')

dceStmt.subject = parse.Transf('''
	dceAssign +
	dceLabel +
	dceReturn +
	dceBlock +
	dceFuncDef
''')

dceStmts.subject = parse.Transf('''
	filterr(try(dceStmt) ; not(?NoStmt))
''')

dceModule = parse.Transf('''
	~Module(<dceStmts>)
''')

dce = scope.Local(
	table.New('nv') &
	dceModule,
	['nv']
)
