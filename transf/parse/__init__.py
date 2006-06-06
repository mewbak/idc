'''Term parsing.'''


__all__ = [
	'Transf',
	'Rule',
]


import sys

try:
	import cStringIO as StringIO
except ImportError:
	import StringIO

from transf.parse.lexer import Lexer
from transf.parse.parser import Parser
from transf.parse.compiler import Walker

def _parser(buf):
	'''Generate a parser for a string buffer.'''
	fp = StringIO.StringIO(buf)
	lexer = Lexer(fp)
	parser = Parser(lexer)
	return parser


def _walker():
	'''Generate a walker passing the caller's caller namespace.'''
	caller = sys._getframe(2)
	walker = Walker(globals=caller.f_globals, locals=caller.f_locals)
	return walker


def Transf(buf):
	'''Parse a transformation from a string.'''
	parser = _parser(buf)
	parser.transf()
	ast = parser.getAST()
	walker = _walker()
	txn = walker.transf(ast)
	return txn


def Rule(buf):
	'''Parse a transformation rule from a string.'''
	parser = _parser(buf)
	parser.rule_def()
	ast = parser.getAST()
	walker = _walker()
	txn = walker.transf(ast)
	return txn

