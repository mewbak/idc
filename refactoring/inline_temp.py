"""Inline Temp"""


from transf import parse
import ir.traverse
import ir.path
import ir.sym


parse.Transfs('''


#######################################################################
# Inline (var, expr) table

shared inline as table

SetVarInline(x, y) =
	inline <= ![x, y] ;
	Where(
		!inline ;
		Filter(inline <= ([z, OnceTD(?x) ] -> [z]))
	)


ClearVarInline(x) = inline <- [x]

clearAllInline = inline <- []

inlineVars = AllTD(?Sym; ~inline)


#######################################################################
# Labels' state

shared label_inline as table

setLabelInline =
Where(
	with label in
		?GoTo(Sym(label)) &
		!inline ;
		Map(![label,<id>,~inline]; label_inline <= ![_,_]) +
		id # FIXME
	end
)

getLabelInline =
Where(
	with label in
		?Label(label) ;
		!label_inline ;
		Filter( ([label,x,y] -> [x,y]) ) ;
		Map(id /inline\ ([x,y] -> <SetVarInline(x, y)>) )
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
		~Assign(_, x, <inlineVars => y>) ;
		if ir.path.isSelected then
			SetVarInline(x, y) ;
			!NoStmt
		else
			Try(ClearVarInline(x))
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
		with label_inline in
			~Function(_, _, _, <
				\label_inline/* with inline in propStmts end
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
	with inline, label_inline in
		propModule
	end


#######################################################################
# Refactoring

applicable =
	ir.path.Applicable(
		ir.path.projectSelection ;
		?Assign(_, Sym(_), _)
		#OnceTD(?Assign(_, Sym(_), _))
	)

input =
	ir.path.Input(
		![]
	)

apply =
	ir.path.Apply(
		[root] -> root ;
		prop
	)


#######################################################################
# Tests

testApply =
	!Module([
		Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
		Assign(Int(32,Signed),Sym("ebx"),Sym("eax"))
	]) ;
	ir.path.annotate ;
	apply [_, [[0,0]]] ;
	?Module([
		Assign(Int(32,Signed),Sym("ebx"),Lit(Int(32,Signed),1))
	])


''')
