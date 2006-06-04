'''Term parsing.'''


import sys

try:
	import cStringIO as StringIO
except ImportError:
	import StringIO

from transf.grammar.lexer import Lexer
from transf.grammar.parser import Parser
from transf.grammar.compiler import Walker


def ParseTransf(buf):
	"""Parse a transformation from a string."""
	
	fp = StringIO.StringIO(buf)
	
	lexer = Lexer(fp)
	parser = Parser(lexer)
	parser.transf()
	ast = parser.getAST()
	#sys.stderr.write(ast.toStringTree() + '\n')
	
	# use caller namespace
	caller = sys._getframe(1)
	walker = Walker(globals=caller.f_globals, locals=caller.f_locals)
	txn = walker.transf(ast)
	
	return txn


def ParseRule(buf):
	"""Parse a transformation rule from a string."""
	
	fp = StringIO.StringIO(buf)
	
	lexer = Lexer(fp)
	parser = Parser(lexer)
	parser.rule_def()
	ast = parser.getAST()
	#sys.stderr.write(ast.toStringTree() + '\n')
	
	# use caller namespace
	caller = sys._getframe(1)
	walker = Walker(globals=caller.f_globals, locals=caller.f_locals)
	txn = walker.transf(ast)
	
	return txn


if __name__ == '__main__':
	# TODO: move these to a test case
	sys.stdout = sys.stderr
	import transf.combinators
	from transf.combinators import Ident as MyIdent
	testCases = [
		'id',
		'fail',
		'id ; fail',
		'id + fail',
		'id + fail ; id',
		'(id + fail) ; id',
		'?1',
		'?0.1',
		'?"s"',
		'?[]',
		'?[1,2]',
		'?C',
		'?C(1,2)',
		'?_',
		'?_(_,_)',
		'?x',
		'?f(x,y)',
		'!1',
		'!0.1',
		'!"s"',
		'![]',
		'![1,2]',
		'!C',
		'!C(1,2)',
		'!_',
		'!_(_,_)',
		'!x',
		'!f(x,y)',
		'?C(<id>,<fail>)',
		'!C(<id>,<fail>)',
		'Ident()',
		'MyIdent()',
		'transf.combinators.Ident()',
		'( C(x,y) -> D(y,x) )',
		'{ C(x,y) -> D(y,x) }',
		'{x, y: id }',
		'<id> 123',
		'id => 123',
		'<id> 1 => 123',
		'!"," => sep',
		'where(!"," => sep)',
		'where( !"," => sep ); id',
		'{ sep : where( !"," => sep ); id }',
		'~C(1, <id>)',
	]
	for input in testCases:
		sys.stderr.write(input + '\n')
		output = repr(ParseTransf(input))
		sys.stderr.write('\t' + output + '\n')
	