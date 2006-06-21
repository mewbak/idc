

import transf as trf


def ApplName(name):
	return trf.match.Appl(trf.match.Str(name), trf.base.ident)


#######################################################################
# Expression

aSym = ApplName('Sym')


#######################################################################
# Statements

aModule = ApplName('Module')
aFunc = ApplName('Func')
aWhile = ApplName('While')
anIf = ApplName('If')
aBlock = ApplName('Block')
aLabel = ApplName('Label')



def Module(stmts = None):
	return trf.match.Appl(
		trf.match.Str('Module'), 
		trf.match.List((stmts,))
	)

def ModuleStmt(stmt, Subterms = trf.lists.Map):
	return Module(Subterms(stmt))


def Func(type = None, name = None, args = None, stmts = None):
	return trf.match.Appl(
		trf.match.Str('Func'), 
		trf.match.List((type, name, args, stmts))
	)


def Block(stmts = None):
	return trf.match.Appl(
		trf.match.Str('Block'), 
		trf.match.List((stmts))
	)


def If(cond = None, true = None, false = None):
	return trf.match.Appl(
		trf.match.Str('Block'), 
		trf.match.List((stmts))
	)

def matchApplName(names):
	return match.Appl(match.StrSet(*names), base.ident)
	
