'''Constant/expression propagation.'''


from transf import *
import ir.match
import ir.sym
import ir.dce


parse.Transfs(r'''
hasSideEffects = OnceTD(?Call + ?Sym ; Not(ir.sym.isLocalVar))
''')


#######################################################################
# Inline (var, expr) table

parse.Transfs(r'''

SetVarInline(x, y) = 
	Where(![x, y] ==> inline) ;
	Where(
		!inline ;
		Filter(([z, OnceTD(?x) ] -> [z]) ==> inline)
	)
	

ClearVarInline(x) = Where(![x] ==> inline)

clearAllInline = Where(![] ==> inline)

inlineVars = AllTD(?Sym; ~inline)


''')

#######################################################################
# Labels' state

parse.Transfs(r'''
setLabelInline =
Where(
	with label in
		?GoTo(Sym(label)) <
		!inline ; 
		Map(![label,<id>,~inline]; ![_,_] ==> label_inline) +
		id # FIXME
	end
)

setLabelInline = id

getLabelInline =
Where(
	with label in
		?Label(label) ; debug.Dump(); 
		!label_inline ; Filter( ([label,x,y] -> [x,y]) ) ;
		Map(id /inline\ ([x,y] -> <SetVarInline(!x, !y)>) )
	end
)

getLabelInline = clearAllInline

''')

#######################################################################
# Statements

parse.Transfs(r'''
propStmt = Proxy()
propStmts = Proxy()

propAssign = 
	with x, y in
		~Assign(_, x, y@<inlineVars>) ;
		if <ir.sym.isLocalVar> x then
			if <hasSideEffects> y then
				debug.Log(`'******* has side effects %s\n'`, !y) ;
				ClearVarInline(!x)
			else
				debug.Log(`'*******  %s\n'`, !x) ;
				SetVarInline(!x, !y)
			end
		end
	end 

propAsm = 
	?Asm ;
	clearAllInline

propLabel = 
	?Label ;
	getLabelInline

propGoTo = 
	?GoTo(<inlineVars>) ;
	setLabelInline

propRet = 
	?Ret(_, <inlineVars>)

propBlock = 
	~Block(<propStmts>)

propIf = 
	~If(<inlineVars>, _, _) ;
	~If(_, <propStmt>, _) /inline\ ~If(_, _, <propStmt>)

propWhile = 
	/inline\* ~While(<inlineVars>, <propStmt>)

propFunction = 
	ir.sym.EnterFunction(
		with label_inline[] in
			~Function(_, _, _, <
				\label_inline/* with inline[] in propStmts end 
			>)
			; debug.Dump()
		end
	)

propDefault = 
	clearAllInline

propStmt.subject = 
	?Assign < propAssign +
	?Asm < propAsm +
	?Label < propLabel +
	?GoTo < propGoTo +
	?Ret < propRet +
	?Block < propBlock +
	?If < propIf +
	?While < propWhile +
	?Function < propFunction + 
	?Var < id +
	?NoStmt

propStmts.subject = 
	Map(propStmt)

propModule = 
	ir.sym.EnterModule(
		~Module(<propStmts>)
	)

prop =
	with inline[], local[], label_inline[] in
		propModule
	end
''')

prop = prop
