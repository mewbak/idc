'''Matching tranformations.'''


import transf as lib


#######################################################################
# Utilities

def ApplName(name):
	return lib.match.Appl(lib.match.Str(name), lib.base.ident)

def ApplNames(names):
	return lib.match.Appl(lib.match.StrSet(*names), lib.base.ident)


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

matchType = ApplNames(typeNames)


#######################################################################
# Expressions

aSym = ApplName('Sym')

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

expr = ApplNames(exprNames)


#######################################################################
# Statements

aModule = ApplName('Module')
aFunc = ApplName('Func')
aWhile = ApplName('While')
anIf = ApplName('If')
aBlock = ApplName('Block')
aLabel = ApplName('Label')



def Module(stmts = None):
	return lib.match.Appl(
		lib.match.Str('Module'), 
		lib.match.List((stmts,))
	)

def ModuleStmt(stmt, Subterms = lib.lists.Map):
	return Module(Subterms(stmt))


def Func(type = None, name = None, args = None, stmts = None):
	return lib.match.Appl(
		lib.match.Str('Func'), 
		lib.match.List((type, name, args, stmts))
	)


def Block(stmts = None):
	return lib.match.Appl(
		lib.match.Str('Block'), 
		lib.match.List((stmts))
	)


def If(cond = None, true = None, false = None):
	return lib.match.Appl(
		lib.match.Str('Block'), 
		lib.match.List((true, false,))
	)


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

anAtomStmt = ApplNames(atomStmtNames)
aCompoundStmt = ApplNames(compoundStmtNames)
aStmt = ApplNames(stmtNames)

# list a statement's sub-statements
reduceStmts = lib.parse.Transf('''
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

stopStmts = -(aModule + aCompoundStmt + lib.match.aList)





