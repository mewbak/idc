'''Matching tranformations.'''


import transf as lib


#######################################################################
# Types

typeNames = [
	'Void',
	'Bool',
	'Int',
	'Float',
	'Char',
	'Pointer',
	'Array',
	'Compound',
	'Union',
	'Function',
	'Blob',
]

matchType = lib.match.ApplNames(typeNames)


#######################################################################
# Expressions

aSym = lib.match.ApplName('Sym')

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

expr = lib.match.ApplNames(exprNames)


#######################################################################
# Statements

aModule = lib.match.ApplName('Module')
aFunction = lib.match.ApplName('Function')
aWhile = lib.match.ApplName('While')
anIf = lib.match.ApplName('If')
aBlock = lib.match.ApplName('Block')
aLabel = lib.match.ApplName('Label')



def Module(stmts = lib.base.ident):
	return lib.match.Appl('Module', (stmts,))

def ModuleStmt(stmt, Subterms = lib.lists.Map):
	return Module(Subterms(stmt))


def Function(type = lib.base.ident, name = lib.base.ident, args = lib.base.ident, stmts = lib.base.ident):
	return lib.match.Appl('Function', (type, name, args, stmts))


def Block(stmts = lib.base.ident):
	return lib.match.Appl('Block', (stmts,))


def If(cond = lib.base.ident, true = lib.base.ident, false = lib.base.ident):
	return lib.match.Appl('If', (cond, true, false))


# names of non-comound statements
atomStmtNames = [
	'Asm',
	'Assign',
	'Var',
	'Ret',
	'Label',
	'GoTo',
	'Break',
	'Continue',
	'NoStmt'
]

# names of compound statements
compoundStmtNames = [
	'Block',
	'Function',
	'If',
	'Module',
	'While',
]

stmtNames = atomStmtNames + compoundStmtNames

anAtomStmt = lib.match.ApplNames(atomStmtNames)
aCompoundStmt = lib.match.ApplNames(compoundStmtNames)
aStmt = lib.match.ApplNames(stmtNames)

# list a statement's sub-statements
reduceStmts = lib.parse.Transf('''
{ stmts:
	( 
		?Block(stmts) +
		?If(_, *stmts) +
		?While(_, *stmts) +
		?Function(_,_,_,stmts) +
		?Module(stmts)
	) ; !stmts +
	![]
}
''')

stopStmts = -(aModule + aCompoundStmt + lib.match.aList)





