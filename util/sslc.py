#!/usr/bin/env python


import sys
import optparse
import os.path

import aterm.factory

from lang.ssl.lexer import Lexer
from lang.ssl.parser import Parser
from lang.ssl.preprocessor import Walker as Preprocessor
from lang.ssl.compiler import Walker as Compiler


def sslc(fpin, fpout, debug = False):
	lexer = Lexer(fpin)
	lexer.setFilename(fpin.name)

	parser = Parser(lexer)
	parser.setFilename(fpin.name)

	parser.start()
	ast = parser.getAST()

	preprocessor = Preprocessor()
	preprocessor.start(ast)
	ast = preprocessor.getAST()

	if debug:
		sys.stderr.write("*** AST begin ***\n")
		sys.stderr.write(ast.toStringList())
		sys.stderr.write("\n")
		sys.stderr.write("*** AST end ***\n")

	factory = aterm.factory.factory

	compiler = Compiler(factory, fpout, debug = debug)
	compiler.start(ast)


def main():
	parser = optparse.OptionParser(
		usage = "\n\t%prog [options] file ...", 
		version = "%prog 1.0")
	parser.add_option(
		"-d", "--debug", 
		action = "store_true", dest = "debug", default = False, 
		help = "show debugging info")
	parser.add_option(
		"-o", "--output", 
		type = "string", dest = "output", 
		help = "specify output file")
	(options, args) = parser.parse_args(sys.argv[1:])
	
	for arg in args:
		fpin = file(arg, "rt")
	
		if options.output is None:
			root, ext = os.path.splitext(arg)
			fpout = file(root + ".py", "wt")
		elif options.output is "-":
			fpout = sys.stdout
		else:
			fpout = file(options.output, "wt")
	
		sslc(fpin, fpout, options.debug)


if __name__ == '__main__':
	main()