"""Inline Temp"""


from transf import lib
import ir.traverse
import ir.path


lib.parse.Transfs('''


#######################################################################
# Inline (var, expr) table


SetVarInline(x, y) =
	Where(![x, y] ==> inline) ;
	Where(
		!inline ;
		Filter(([z, OnceTD(?x) ] -> [z]) ==> inline)
	)


ClearVarInline(x) = Where(![x] ==> inline)

clearAllInline = Where(![] ==> inline)

inlineVars = AllTD(?Sym; ~inline)


#######################################################################
# Labels' state


setLabelInline =
Where(
	with label in
		?GoTo(Sym(label)) <
		!inline ;
		Map(![label,<id>,~inline]; ![_,_] ==> label_inline) +
		id # FIXME
	end
)

getLabelInline =
Where(
	with label in
		?Label(label) ;
		!label_inline ;
		Filter( ([label,x,y] -> [x,y]) ) ;
		Map(id /inline\ ([x,y] -> <SetVarInline(!x, !y)>) )
	end
)


#######################################################################
# Statements

propStmt = Proxy()

propStmts =
	Map(propStmt) ;
	Filter(Not(?NoStmt))

propAssign =
	with x, y in
		~Assign(_, x, y@<inlineVars>) ;
		if ir.path.isSelected then
			SetVarInline(!x, !y) ;
			!NoStmt
		else
			Try(ClearVarInline(!x))
		end
	end

propAsm =
	?Asm ;
	clearAllInline

propLabel =
	?Label ;
	getLabelInline

propGoTo =
	~GoTo(<inlineVars>) ;
	setLabelInline

propRet =
	~Ret(_, <inlineVars>)

propBlock =
	~Block(<propStmts>)

propIf =
	~If(<inlineVars>, _, _) ;
	~If(_, <propStmt>, _) /inline\ ~If(_, _, <propStmt>)

propWhile =
	/inline\* ~While(<inlineVars>, <propStmt>)

propDoWhile =
	/inline\* (
		~DoWhile(_, <propStmt>) ;
		~DoWhile(<inlineVars>, _)
	)

propFunction =
	ir.sym.EnterFunction(
		with label_inline[] in
			~Function(_, _, _, <
				\label_inline/* with inline[] in propStmts end
			>)
		end
	)

propDefault =
	clearAllInline

propStmt.subject =
	switch project.name
		case "Assign": propAssign
		case "Asm": propAsm
		case "Label": propLabel
		case "GoTo": propGoTo
		case "Block": propBlock
		case "If": propIf
		case "While": propWhile
		case "DoWhile": propDoWhile
		case "Function": propFunction
		case "Ret": propRet
		case "Break", "Continue", "NoStmt": id
	end

propModule =
	ir.sym.EnterModule(
		~Module(<propStmts>)
	)

prop =
	with inline[], label_inline[] in
		propModule
	end


#######################################################################
# Refactoring

applicable =
	ir.path.projectSelection ;
	?Assign(_, Sym(_), _)
	#OnceTD(?Assign(_, Sym(_), _))

input =
	![]

apply =
	prop

''')
