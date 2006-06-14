'''Dead Code Elimination.'''


from transf import *


setUnneededVar = table.Del('nv', base.ident)
setNeededVar = table.Set('nv', base.ident, base.ident)
setNeededVars = parse.Transf('''
	alltd(?Sym(<setNeededVar>))
''')
setAllUnneededVars = table.Clear('nv')
isVarNeeded = table.Get('nv', base.ident)
isVarNeeded = debug.Trace('isVarNeeded', isVarNeeded)

JoinNeededVars = lambda l,r: table.Merge(l, r, ['nv'], [])

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

dceLabel = parse.Transf('''
	?Label(*)
''')

dceReturn = parse.Transf('''
	?Ret(*) ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)
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
	~FuncDef(_, _, _, <setAllUnneededVars; dceStmt>)
''')

dceStmt.subject = parse.Transf('''
	dceAssign +
	dceLabel +
	dceReturn +
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
	table.New('nv') &
	dceModule,
	['nv']
)
