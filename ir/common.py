'''Common transformations.'''


from transf import *


#######################################################################
# Utils

def matchApplName(names):
	return match.Appl(match.StrSet(*names), base.ident)
	

#######################################################################
# Module

matchModule = match.Appl(match.Str('Module'), base.ident)


#######################################################################
# Statements

# names of non-comound statements
atomStmtNames = [
	'Asm',
	'Assign',
	'Var',
	'Ret',
	'Label',
	'Jump',
	'Break',
	'Continue',
	'NoStmt'
]

# names of compound statements
compoundStmtNames = [
	'Block',
	'Func',
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
		?Func(_,_,_,stmts) +
		?Module(stmts)
	) ; !stmts +
	![]
}
''')

stopStmts = -(matchModule + matchCompoundStmt + match.aList)

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


#######################################################################
# Types

typeNames = [
	'Void'
	'Bool'
	'Int',
	'Float',
	'Char',
	'Pointer',
	'Array',
	'Compound',
	'Union',
	'Func',
	'Blob',
]

matchType = matchApplName(typeNames)
