'''Common transformations.'''


import transf as trf
import ir.match


def Traverse(subterms, down = None, up = None, stop = None, Enter = None, Leave = None):
	'''Generic traversal.'''
	traverse = subterms
	if Leave is not None:
		traverse = Leave(traverse)
	if stop is not None:
		traverse = stop + traverse
	if up is not None:
		traverse = traverse * up
	if down is not None:
		traverse = down * traverse
	if Enter is not None:
		traverse = Enter(traverse)
	return traverse


def Module(stmts = None, **kargs):
	return Traverse(
		trf.congruent.Appl(
			trf.match.Str('Module'), 
			trf.congruent.List((stmts,))
		),
		**kargs
	)


def Func(type = None, name = None, args = None, stmts = None, **kargs):
	return Traverse(
		trf.congruent.Appl(
			trf.match.Str('Func'), 
			trf.congruent.List((type, name, args, stmts))
		),
		**kargs
	)


def While(cond = None, stmt = None, **kargs):
	return Traverse(
		trf.congruent.Appl(
			trf.match.Str('While'), 
			trf.congruent.List((cond, stmt))
		),
		**kargs
	)


def If(cond = None, true = None, false = None, **kargs):
	return Traverse(
		trf.congruent.Appl(
			trf.match.Str('If'), 
			trf.congruent.List((cond, true, false))
		),
		**kargs
	)


def Block(stmts = None, **kargs):
	return Traverse(
		trf.congruent.Appl(
			trf.match.Str('Block'), 
			trf.congruent.List((stmts,))
		),
		**kargs
	)


def Stmt(stmt, stmts, default, **kargs):
	return Traverse(
		ir.match.aBlock **Block(stmts)**
		ir.match.anIf **If(None, stmt, stmt)**
		ir.match.aWhile **While(None, stmt)**
		ir.match.aFunc **Func(None, None, None, stmts)**
		ir.match.aModule **Module(stmts)**
		default,
		**kargs
	)

def AllStmts(**kargs):
	stmt = trf.util.Proxy()
	stmts = trf.lists.Map(stmt)
	stmt.subject = Stmt(stmt, stmts, trf.base.ident, **kargs)
	return stmt


def AllStmtsBU(up):
	return AllStmts(up = up)


def OneStmt(pre, post = trf.base.ident):
	stmt = trf.util.Proxy()
	stmts = trf.lists.Fetch(stmt)
	stmt.subject = pre ** post ** Stmt(stmt, stmts, trf.base.fail)
	return stmt


def AllGlobalStmts(operand):
	return Module(
		trf.lists.Map(operand)
	)

def OneGlobalStmt(operand):
	return Module(
		trf.lists.Fetch(operand)
	)

def OneFunc(operand, type = None, name = None, args = None, stmts = None):
	return OneGlobalStmt(
		ir.match.Func(type, name, args, stmts), 
		operand
	)


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.factory
	for arg in sys.argv[1:]:
		print "* Reading aterm"
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( pprint2.module * renderBox )(term)
		#print

		#print AllStmts(up = trf.debug.Dump() * trf.annotation.Set('X')) (term)
		print OneStmt(trf.debug.Dump() * ir.match.aLabel * trf.annotation.Set('X')) (term)


if __name__ == '__main__':
	main()
