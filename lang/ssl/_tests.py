#!/usr/bin/env python


import sys
import unittest
import os
import os.path

import antlr

from aterm.factory import factory
from lang.ssl.lexer import Lexer
from lang.ssl.parser import Parser


class TestCase(unittest.TestCase):
	
	def setUp(self):
		ssldir = 'lang/ssl/spec' 
		self.filenames = [os.path.join(ssldir, file) for file in os.listdir(ssldir) if file.endswith('.ssl')]

	def testLexer(self):
		for filename in self.filenames:
			lexer = Lexer(file(filename, 'rt'))
			
			try:
				for token in lexer:
					pass
			except antlr.TokenStreamException, ex:
				self.fail('%s: exception caught while lexing: %s', ex)
			
	def testParser(self):
		for filename in self.filenames:
			lexer = Lexer(file(filename, 'rt'))
			parser = Parser(lexer, factory=factory)
			parser.setFilename(filename)
			parser.start()
			parser.getAST()


if __name__ == '__main__':
	unittest.main()
