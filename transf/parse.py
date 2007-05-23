'''Transformation parsing.'''


import sys

from antlraterm import Walker as Converter
from lang.transf.lexer import Lexer
from lang.transf.parser import Parser
from lang.transf.compiler import Compiler


_converter = Converter()


def _parser(buf):
	'''Generate a parser for a string buffer.'''
	lexer = Lexer(buf)
	parser = Parser(lexer)
	return parser


def _compile(buf, method, simplify=True):
	parser = _parser(buf)
	getattr(parser, method)()
	ast = parser.getAST()
	term = _converter.aterm(ast)
	if False:
		# FIXME: re-enable the simplifier
		import lang.transf.simplifier
		old = term
		term = lang.transf.simplifier.simplify(term)
	compiler = Compiler()
	code = getattr(compiler, method)(term)
	return code


def _populate_globals(glbls):
	"""Populate the global namespace."""
	# TODO: reduce the name polution
	import transf
	glbls.setdefault('transf', transf)
	from transf import lib
	for n, v in lib.__dict__.iteritems():
		glbls.setdefault(n, v)
	from lang.transf import builtins
	for n, v in builtins.__dict__.iteritems():
		glbls.setdefault(n, v)
	return glbls


def _eval(code):
	'''Eval the compiled code in the caller's namespace.'''
	caller = sys._getframe(2)
	globals_ = _populate_globals(caller.f_globals)
	locals_ = caller.f_locals
	try:
		txn = eval(code, globals_, locals_)
	except:
		sys.stderr.write("input code: %s\n" % code)
		raise
	return txn


def _exec(code):
	'''Execute the compiled code in the caller's namespace.'''
	caller = sys._getframe(2)
	globals_ = _populate_globals(caller.f_globals)
	locals_ = caller.f_locals
	try:
		exec code in globals_, locals_
	except:
		sys.stderr.write("input code: %s\n" % code)
		raise


def Transfs(buf, simplify=True):
	'''Parse transformation definitions from a string.'''
	code = _compile(buf, "transf_defs", simplify)
	_exec(code)


def Transf(buf, simplify=True):
	'''Parse a transformation from a string.'''
	code = _compile(buf, "transf", simplify)
	txn = _eval(code)
	return txn
