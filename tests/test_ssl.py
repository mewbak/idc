#!/usr/bin/env python


import sys
import unittest
import os
import os.path

import antlr

sys.path.insert(0,'util/sslc')

from aterm.factory import factory
from lexer import Lexer
from parser import Parser


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.filenames = [os.path.join('ssl', file) for file in os.listdir('ssl') if file.endswith('.ssl')]

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
