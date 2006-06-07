'''Pretty-printing of intermediate representation code.
'''


from transf import base
from transf import strings
from transf import parse


def Type(typer):
	typet = base.Proxy()
	typet.subject = parse.Transf('''
		~Pointer(_, <typet>) +
		~Array(<typet>) +
		id
	''') & typer
	return typet


def Expr(exprr, typet, opr):
	exprt = base.Proxy()
	exprt.subject = parse.Transf('''
		~Lit(<typet>, _) +
		~Cast(<typet>, <exprt>) +
		~Unary(<opr>, <exprt>) +
		~Binary(<opr>, <exprt>, <exprt>) +
		~Cond(<exprt>, <exprt>, <exprt>) +
		~Call(<exprt>, <map(exprt)>) +
		~Addr(<exprt>) +
		~Ref(<exprt>) +
		id
	''') & exprr
	return exprt


def Stmt(stmtr, exprt, typet):
	stmtt = base.Proxy()
	stmtt.subject = parse.Transf('''
		~Assign(<typet>, <exprt>, <exprt>) +
		~Asm(_, <map(exprt)>) +
		~Block(<map(stmtt)>) +
		~FuncDef(<typet>, _, _, <stmtt>) +
		~If(<exprt>, <stmtt>, <stmtt>) +
		~While(<exprt>, <stmtt>) +
		~Ret(<typet>, <exprt>) +
		~Branch(<exprt>) +
		id
	''') & stmtr
	return stmtt


def Module(moduler, stmtt):
	modulet = parse.Transf('''
		~Module(<map(stmtt)>)
	''') & moduler
	return modulet
	
