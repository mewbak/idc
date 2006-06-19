'''Transformations for traversing IR code.
'''


from transf import base
from transf import util
from transf import strings
from transf import parse
from transf import traverse


def DOWN(down):
	return lambda traverser: down & traverser

def UP(up):
	return lambda traverser: traverser & up

def DOWNUP(down, up):
	return lambda traverser: down & traverser & up


def Type(Wrapper = None):
	'''Create a type traverser.'''

	type = util.Proxy()
	type.subject = parse.Transf('''
		~Pointer(_, <type>) +
		~Array(<type>) +
		id
	''')
	
	if Wrapper is not None:
		type.subject = Wrapper(type.subject)
	
	return type


def Expr(type = None, op = None, Wrapper = None):
	'''Create an expression traverser.'''

	if type is None:
		type = base.ident
	if op is None:
		op = base.ident
		
	expr = util.Proxy()
	expr.subject = parse.Transf('''
		~Lit(<type>, _) +
		~Cast(<type>, <expr>) +
		~Unary(<op>, <expr>) +
		~Binary(<op>, <expr>, <expr>) +
		~Cond(<expr>, <expr>, <expr>) +
		~Call(<expr>, <Map(expr)>) +
		~Addr(<expr>) +
		~Ref(<expr>) +
		id
	''')
	
	if Wrapper is not None:
		expr.subject = Wrapper(expr.subject)
		
	return expr


def Stmt(stmts = None, expr = None, type = None, Wrapper = None):
	'''Create a statement traverser.'''
	
	stmt = util.Proxy()
	
	if expr is None:
		expr = base.ident
	if type is None:
		type = base.ident
	if stmts is None:
		stmts = traverse.Map(stmt)
		
	stmt.subject = parse.Transf('''
		~Var(<type>, _, <expr>) +
		~Func(<type>, _, _, <stmts>) +
		~Assign(<type>, <expr>, <expr>) +
		~Asm(_, <Map(expr)>) +
		~Block(<stmts>) +
		~Func(<type>, _, _, <stmt>) +
		~If(<expr>, <stmt>, <stmt>) +
		~While(<expr>, <stmt>) +
		~Ret(<type>, <expr>) +
		~Jump(<expr>) +
		id
	''')
	
	if Wrapper is not None:
		stmt.subject = Wrapper(stmt.subject)
	
	return stmt


def Module(stmt = None, stmts = None, Wrapper = None):
	'''Create a module traverser.'''
	
	if stmts is None:
		if stmt is not None :
			stmts = traverse.Map(stmt)
		else:
			stmts = base.ident
		
	module = parse.Transf('''
		~Module(<stmts>)
	''')
	
	if Wrapper is not None:
		module = Wrapper(module)
		
	return module

