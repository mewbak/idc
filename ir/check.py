'''Intermediate code correctness checking.
'''


import sys

from transf import transformation
from transf import lib
from transf import parse


class LogFail(transformation.Transformation):

	def __init__(self, msg):
		transformation.Transformation.__init__(self)
		self.msg = msg

	def apply(self, term, context):
		sys.stderr.write('%s: %r\n' % (self.msg, term))
		raise exception.Failure


if __name__ != '__main__':
	LogFail = lambda msg: lib.base.fail


parse.Transfs('''

name = lib.match.aStr

size = lib.match.anInt

lit =
	lib.match.anInt +
	lib.match.aReal +
	lib.match.aStr

sign =
	?Signed +
	?Unsigned +
	?NoSign +
	LogFail(`'bad sign'`)

types = lib.lists.Map(type)
type =
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
	?Blob( <size> ) +
	LogFail(`'bad type'`)

unOp =
	?Not( <type> ) +
	?Neg( <type> ) +
	LogFail(`'bad unary operator'`)

binOp =
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
	?GtEq( <type> ) +
	LogFail(`'bad binary operator'`)

addr = expr
exprs = lib.lists.Map(expr)
expr =
	?Lit( <type> , <lit> ) +
	?Sym( <name> ) +
	?Cast( <type> , <expr> ) +
	?Unary( <unOp>, <expr> ) +
	?Binary( <binOp>, <expr> , <expr> ) +
	?Cond( <expr> , <expr> , <expr> ) +
	?Call( <addr> , <exprs> ) +
	?Addr( <expr> ) +
	?Ref( <addr> ) +
	LogFail(`'bad expression'`)

optExpr =
	?NoExpr +
	expr

arg =
	?Arg( <type> , <name> ) +
	LogFail(`'bad argument'`)

stmts = lib.lists.Map(stmt)
stmt =
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
	?NoStmt +
	LogFail(`'bad statement'`)

module =
	?Module( <stmts> ) +
	LogFail(`'bad module'`)
''')

if __name__ == '__main__':
	import aterm.factory
	import sys

	factory = aterm.factory.factory

	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))
		sys.stderr.write('Checking %s ...\n' % arg)
		try:
			module(term)
		except exception.Failure:
			sys.stderr.write('FAILED\n')
		else:
			sys.stderr.write('OK\n')
		sys.stderr.write('\n')


