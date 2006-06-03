'''Term parsing.'''


import sys


def Parse(buf):
	"""Parse a string."""
	
	try:
		from cStringIO import StringIO
	except ImportError:
		from StringIO import StringIO
	
	fp = StringIO(buf)
	
	from transf.grammar.lexer import Lexer
	from transf.grammar.parser import Parser
	from transf.grammar.compiler import Walker

	lexer = Lexer(fp)
	parser = Parser(lexer)
	parser.grammar()
	ast = parser.getAST()
	sys.stderr.write(ast.toStringTree() + '\n')
	
	# use caller namespace
	caller = sys._getframe(1)
	walker = Walker(globals=caller.f_globals, locals=caller.f_locals)
	txn = walker.transf(ast)
	
	return txn


if __name__ == '__main__':
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
		'transf.combinators.Ident()'
	]
	for input in testCases:
		sys.stderr.write(input + '\n')
		output = repr(Parse(input))
		sys.stderr.write('\t' + output + '\n')
	