'''Intermediate code correctness checking.
'''


import sys

import transf


class LogFail(transf.base.Transformation):

	def __init__(self, msg):
		transf.base.Transformation.__init__(self)
		self.msg = msg
	
	def apply(self, term, context):
		sys.stderr.write('%s: %r\n' % (self.msg, term))
		raise transf.exception.Failure


if __name__ != '__main__':
	LogFail = lambda msg: transf.base.fail


name = transf.match.aStr

size = transf.match.anInt

lit = transf.match.anInt + transf.match.aReal + transf.match.aStr

sign = transf.parse.Transf('''
	?Signed +
	?Unsigned +
	?NoSign
''') + LogFail('bad sign')

type = transf.util.Proxy()
types = transf.lists.Map(type)
type.subject = transf.parse.Transf('''
	?Void +
	?Bool +
	?Int( <size>, <sign> ) +
	?Float( <size> ) +
	?Char( <size> ) +
	?Pointer( <size>, <types> ) +
	?FuncPointer( <type>, <types> ) +
	?Array( <type> ) +
	?Compound( <types> ) +
	?Union( <types> ) +
	?Blob( <size> )
''') + LogFail('bad type')

unOp = transf.parse.Transf('''
	?Not( <type> ) +
	?Neg( <type> )
''') + LogFail('bad unary operator')

binOp = transf.parse.Transf('''
	?And( <type> ) +
	?Or( <type> ) +
	?Xor( <type> ) +
	?LShift( <type> ) +
	?RShift( <type> ) +
	
	?Plus( <type> ) +
	?Minus( <type> ) +
	?Mult( <type> ) +
	?Div( <type> ) +
	?Mod( <type> ) +
	
	?Eq( <type> ) +
	?NotEq( <type> ) +
	?Lt( <type> ) +
	?LtEq( <type> ) +
	?Gt( <type> ) +
	?GtEq( <type> )
''') + LogFail('bad binary operator')

expr = transf.util.Proxy()
addr = expr
exprs = transf.lists.Map(expr)
expr.subject = transf.parse.Transf('''
	?Lit( <type> , <lit> ) +
	?Sym( <name> ) +
	?Cast( <type> , <expr> ) +
	?Unary( <unOp>, <expr> ) +
	?Binary( <binOp>, <expr> , <expr> ) +
	?Cond( <expr> , <expr> , <expr> ) +
	?Call( <addr> , <exprs> ) +
	?Addr( <expr> ) +
	?Ref( <addr> )
''') + LogFail('bad expression')

optExpr = transf.parse.Transf('''
	?NoExpr +
	expr
''')

arg = transf.parse.Transf('''
	?Arg( <type> , <name> )
''') + LogFail('bad argument')
	
stmt = transf.util.Proxy()
stmts = transf.lists.Map(stmt)
stmt.subject = transf.parse.Transf('''
	?Var( <type> , <name> , <optExpr> ) +
	?Function( <type> , <name> , <Map(arg)>, <stmts> ) +
	?Assign( <type> , <optExpr> , <expr> ) +
	?If( <expr> , <stmt> , <stmt> ) +
	?While( <expr> , <stmt> ) +
	?DoWhile( <expr> , <stmt> ) +
	?Block( <stmts> ) +
	?Ret( <type> , <optExpr> ) +
	?Label( <name> ) +
	?Asm( <name> , <exprs> ) +
	?GoTo( <addr> ) +
	?Break +
	?Continue +
	?NoStmt
''') + LogFail('bad statement')

module = transf.parse.Transf('''
	?Module( <stmts> )
''') + LogFail('bad module')


if __name__ == '__main__':
	import aterm.factory
	import sys
	
	factory = aterm.factory.factory
	
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))
		sys.stderr.write('Checking %s ...\n' % arg)
		try:
			module(term)
		except transf.exception.Failure:
			sys.stderr.write('FAILED\n')
		else:
			sys.stderr.write('OK\n')
		sys.stderr.write('\n')
		

