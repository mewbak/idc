'''Common transformations.'''


from transf import *


#######################################################################
# Utils

def matchApplName(names):
	return match.Appl(match.StrSet(*names), base.ident)
	

#######################################################################
# Statements

# names of non-comound statements
atomStmtNames = [
	'Asm',
	'Assign',
	'VarDef',
	'Ret',
	'Label',
	'Branch',
	'Break',
	'Continue',
	'NoStmt'
]

# names of compound statements
compoundStmtNames = [
	'Block',
	'Funcdef',
	'If',
	'Module',
	'While',
]

stmtNames = atomStmtNames + compoundStmtNames

matchAtomStmt = matchApplName(atomStmtNames)
matchCompoundStmt = matchApplName(compoundStmtNames)
matchStmt = matchApplName(stmtNames)

# list a statement's sub-statements
reduceStmts = parse.Transf('''
{ stmts:
	( 
		?Block(stmts) +
		?If(_, *stmts) +
		?While(_, *stmts) +
		?FuncDef(_,_,_,*stmts) +
		?Module(stmts)
	) ; !stmts +
	![]
}
''')


#######################################################################
# Expressions

exprNames = [
	'True'
	'False'
	'Lit',
	'Sym',
	'Cast',
	'Unary',
	'Binary',
	'Cond',
	'Call',
	'Cast',
	'Addr',
	'Ref',
]

matchExpr = matchApplName(exprNames)
