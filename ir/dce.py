'''Dead Code Elimination.'''


from transf import *
import ir.match


#######################################################################
# Local var table

# TODO: detect local variables from scope rules
isReg = combine.Where(annotation.Get('Reg'))
isTmp = combine.Where(annotation.Get('Tmp'))
isLocalVar = ir.match.aSym * (isReg + isTmp)

updateLocalVar = (
	isLocalVar * 
	table.Set('local')
)

updateLocalVars = traverse.AllTD(updateLocalVar)


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

isVarNeeded = ir.match.aSym ; (?needed + Not(isLocalVar))
''')


#######################################################################
# Labels

getLabelNeeded = parse.Transf('''
Where(
	with label in
		?Jump(Sym(label)) <
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
		setAllUnneededVars ;
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

dceAssign = 
	{x:
		?Assign(_, x, _) ;
		if <isLocalVar> x then
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

dceJump = 
	?Jump ;
	getLabelNeeded

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
	with local[], label_needed[] in
		updateLocalVars ;
		~Func(_, _, _, <
#			table.Iterate(with needed[] in dceStmts end, `['label_needed']`, `[]`)
			\label_needed/* with needed[] in dceStmts end 
		>)
		; debug.Dump()
	end

# If none of the above applies, assume all vars are needed
dceDefault = 
	setAllNeededVars

dceStmt.subject = 
	?Assign < dceAssign +
	?Asm < dceAsm +
	?Label < dceLabel +
	?Jump < dceJump +
	?Ret < dceRet +
	?Block < dceBlock +
	?If < dceIf +
	?Func < dceFunc + 
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

