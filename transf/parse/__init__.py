'''Term parsing.'''


import sys

try:
	import cStringIO as StringIO
except ImportError:
	import StringIO

from transf.parse.lexer import Lexer
from transf.parse.parser import Parser
from transf.parse.translator import Walker as Translator


__all__ = [
	'Transf',
	'Rule',
]


def _parser(buf):
	'''Generate a parser for a string buffer.'''
	lexer = Lexer(buf)
	parser = Parser(lexer)
	return parser


def _translator():
	'''Generate a walker passing the caller's caller namespace.'''
	caller = sys._getframe(2)
	translator = Translator(globals=caller.f_globals, locals=caller.f_locals)
	return translator


def Transfs(buf):
	'''Parse transformation definitions from a string.'''
	parser = _parser(buf)
	parser.transf_defs()
	ast = parser.getAST()
	translator = _translator()
	translator.transf_defs(ast)


def Transf(buf):
	'''Parse a transformation from a string.'''
	parser = _parser(buf)
	parser.transf()
	ast = parser.getAST()
	translator = _translator()
	txn = translator.transf(ast)
	return txn


def Rules(buf):
	'''Parse rules definitions from a string.'''
	parser = _parser(buf)
	parser.rule_defs()
	ast = parser.getAST()
	translator = _translator()
	txn = translator.transf_defs(ast)
	return txn


def Rule(buf):
	'''Parse a transformation rule from a string.'''
	parser = _parser(buf)
	parser.rule_set()
	ast = parser.getAST()
	translator = _translator()
	txn = translator.transf(ast)
	return txn

