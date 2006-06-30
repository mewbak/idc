'''Dead Code Elimination.'''


from transf import *
import ir.match
import ir.sym


#######################################################################
# Needed/uneeded table

setUnneededVar = table.Del('needed')
setNeededVar = table.Set('needed')

setNeededVars = debug.Log('Finding needed vars in %s\n', base.ident) * \
	traverse.AllTD(ir.match.aSym * setNeededVar * 
	debug.Log('Found var needed %s\n', base.ident))

setAllUnneededVars = table.Clear('needed')
setAllNeededVars = table.Add('needed', 'local')

parse.Transfs(r'''

isVarNeeded = ir.match.aSym ; (?needed + Not(ir.sym.isLocalVar))
''')


#######################################################################
# Labels

getLabelNeeded = parse.Transf('''
Where(
	with label in
		?GoTo(Sym(label)) <
			!label_needed ; Map(Try(?[label,<setNeededVar>])) +
			setAllNeededVars
	end
)
''')

setLabelNeeded = parse.Transf('''
Where(
	with label in
		?Label(label) ; debug.Dump(); 
		!needed ; 
		Map(![label,<id>] ; 
		table.Set('label_needed'))
	end
)
''')

#######################################################################
# Statements

parse.Transfs(r'''
dceStmt = Proxy()
dceStmts = Proxy()

dceAssign = {x:
	?Assign(_, x, _) ;
	if <ir.sym.isLocalVar> x then
		if <isVarNeeded> x then
			debug.Log(`'******* var needed %s\n'`, !x) ;
			Where(<setUnneededVar> x );
			~Assign(_, _, <setNeededVars>)
		else
			debug.Log(`'******* var uneeded %s\n'`, !x) ;
			!NoStmt
		end
	else
		debug.Log(`'******* var not local %s\n'`, !x) ;
		~Assign(_, <setNeededVars>, <setNeededVars>)
	end
}

dceAsm = 
	?Asm ;
	setAllNeededVars

dceLabel = 
	?Label ;
	setLabelNeeded

dceGoTo = 
	?GoTo ;
	getLabelNeeded

dceRet = 
	?Ret ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)

elimBlock = {
	Block([]) -> NoStmt
}

dceBlock = 
	~Block(<dceStmts>) ;
	Try(elimBlock)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf = 
	~If(_, <dceStmt>, _) \needed/ ~If(_, _, <dceStmt>) ;
	~If(<setNeededVars>, _, _) ;
	Try(elimIf)

elimWhile = {
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceWhile = 
	\needed/* ~While(<setNeededVars>, <dceStmt>) ;
	Try(elimWhile)

dceFunction = 
	ir.sym.EnterFunction(
	with label_needed[] in
		~Function(_, _, _, <
			\label_needed/* with needed[] in dceStmts end 
		>)
		; debug.Dump()
	end
	)

# If none of the above applies, assume all vars are needed
dceDefault = 
	setAllNeededVars

dceStmt.subject = 
	?Assign < dceAssign +
	?Asm < dceAsm +
	?Label < dceLabel +
	?GoTo < dceGoTo +
	?Ret < dceRet +
	?Block < dceBlock +
	?If < dceIf +
	?While < dceWhile +
	?Function < dceFunction + 
	?Var < id +
	?NoStmt

dceStmts.subject = 
	MapR(dceStmt) ;
	Filter(Not(?NoStmt))

dceModule = 
	~Module(<dceStmts>)

dce =
	with needed[], local[], label_needed[] in
		dceModule
	end
''')

