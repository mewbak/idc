"""Dead Label Elimination"""


from transf import lib


lib.parse.Transfs('''


#######################################################################
# Labels

updateNeededLabels = 
Where(
	with label in
		?GoTo(Sym(label)) ;
		![label,label] ==> needed_label
	end
)

#######################################################################
# Statements

dceStmt = Proxy()
dceStmts = Proxy()

dceLabel = 
	Try(
		?Label(<Not(~needed_label)>) ;
		!NoStmt
	)

elimBlock = {
	Block([]) -> NoStmt |
	Block([stmt]) -> stmt
}

dceBlock = 
	~Block(<dceStmts>) ;
	Try(elimBlock)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf = 
	~If(_, <dceStmt>, <dceStmt>) ;
	Try(elimIf)

elimWhile = {
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceWhile = 
	~While(_, <dceStmt>) ;
	Try(elimWhile)

elimDoWhile = {
	DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceDoWhile = 
	~DoWhile(_, <dceStmt>) ;
	Try(elimDoWhile)

dceFunction = 
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		~Function(_, _, _, <dceStmts>)
	end

# If none of the above applies, assume all vars are needed
dceDefault = 
	id

dceStmt.subject = 
	?Label < dceLabel +
	?Block < dceBlock +
	?If < dceIf +
	?While < dceWhile +
	?DoWhile < dceDoWhile +
	?Function < dceFunction + 
	id

dceStmts.subject = 
	MapR(dceStmt) ;
	Filter(Not(?NoStmt))

dceModule = 
	~Module(<dceStmts>)

dce =
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		dceModule
	end


''')
