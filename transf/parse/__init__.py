'''Term parsing.'''


import sys

from transf.parse.lexer import Lexer
from transf.parse.parser import Parser
from antlraterm import Walker as Converter
from transf.parse.translator import Translator


__all__ = [
	'Transf',
	'Rule',
]


_converter = Converter()


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


def Transfs(buf, simplify=True):
	'''Parse transformation definitions from a string.'''
	parser = _parser(buf)
	parser.transf_defs()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	if simplify:
		import transf.parse.simplifier
		old = term
		term = transf.parse.simplifier.simplify(term)
	translator = _translator()
	translator.transf_defs(term)


def Transf(buf):
	'''Parse a transformation from a string.'''
	parser = _parser(buf)
	parser.transf()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	if True:
		import transf.parse.simplifier
		old = term
		term = transf.parse.simplifier.simplify(term)
	translator = _translator()
	txn = translator.transf(term)
	return txn


def Rules(buf):
	'''Parse rules definitions from a string.'''
	parser = _parser(buf)
	parser.rule_defs()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	if True:
		import transf.parse.simplifier
		old = term
		term = transf.parse.simplifier.simplify(term)
	translator = _translator()
	txn = translator.transf_defs(term)
	return txn


def Rule(buf, simplify=True):
	'''Parse a transformation rule from a string.'''
	parser = _parser(buf)
	parser.rule_set()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	if simplify:
		import transf.parse.simplifier
		old = term
		term = transf.parse.simplifier.simplify(term)
	translator = _translator()
	txn = translator.transf(term)
	return txn


def Meta(buf):
	'''Parse a meta transformation from a string.'''
	parser = _parser(buf)
	parser.meta_def()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	translator = _translator()
	txn = translator.meta_def(term)
	return txn


