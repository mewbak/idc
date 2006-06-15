'''Common transformations.'''


from transf import *


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

matchStmt = match.Appl(
	match.StrSet(*(atomStmtNames + compoundStmtNames)),
	base.ident
)

matchAtomStmt = match.Appl(
	match.StrSet(*atomStmtNames),
	base.ident
)

matchCompoundStmt = match.Appl(
	match.StrSet(*compoundStmtNames),
	base.ident
)

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

