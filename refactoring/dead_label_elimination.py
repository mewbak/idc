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

dleStmt = Proxy()
dleStmts = Proxy()

dleLabel =
	Try(
		?Label(<Not(~needed_label)>) ;
		!NoStmt
	)

elimBlock = {
	Block([]) -> NoStmt |
	Block([stmt]) -> stmt
}

dleBlock =
	~Block(<dleStmts>) ;
	Try(elimBlock)

elimIf = {
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dleIf =
	~If(_, <dleStmt>, <dleStmt>) ;
	Try(elimIf)

elimWhile = {
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dleWhile =
	~While(_, <dleStmt>) ;
	Try(elimWhile)

elimDoWhile = {
	DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dleDoWhile =
	~DoWhile(_, <dleStmt>) ;
	Try(elimDoWhile)

dleFunction =
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		~Function(_, _, _, <dleStmts>)
	end

# If none of the above applies, assume all vars are needed
dleDefault =
	id

dleStmt.subject =
	?Label < dleLabel +
	?Block < dleBlock +
	?If < dleIf +
	?While < dleWhile +
	?DoWhile < dleDoWhile +
	?Function < dleFunction +
	id

dleStmts.subject =
	MapR(dleStmt) ;
	Filter(Not(?NoStmt))

dleModule =
	~Module(<dleStmts>)

dle =
	with needed_label[] in
		AllTD(updateNeededLabels) ;
		dleModule
	end


''')
