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


def _compile(buf, method, simplify=True, verbose=False):
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
	if verbose:
		sys.stderr.write("input code:\n%s\n" % buf)
		sys.stderr.write("output code:\n%s\n" % code)
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


def _exec(code, globals_, locals_):
	'''Execute the compiled code in the caller's namespace.'''
	try:
		exec code in globals_, locals_
	except NameError:
		sys.stderr.write("globals: %s\n" % globals_.keys())
		sys.stderr.write("locals: %s\n" % locals_.keys())
		sys.stderr.write("input code:\n%s\n" % code)
		raise
	except:
		sys.stderr.write("input code:\n%s\n" % code)
		raise


def Transfs(buf, simplify=True, verbose=False):
	'''Parse transformation definitions from a string.'''
	code = _compile(buf, "transf_defs", simplify=simplify, verbose=verbose)
	caller = sys._getframe(1)
	globals_ = _populate_globals(caller.f_globals)
	locals_ = caller.f_locals
	_exec(code, globals_, locals_)


def Transf(buf, simplify=True, verbose=False):
	'''Parse a transformation from a string.'''
	code = _compile("_tmp = %s" % buf, "transf_defs", simplify=simplify, verbose=verbose)
	caller = sys._getframe(1)
	globals_ = _populate_globals(caller.f_globals)
	locals_ = caller.f_locals.copy()
	_exec(code, globals_, locals_)
	return locals_["_tmp"]
