'''Module for handling assembly language code.'''

# TODO: redesign this module in order to cope with more than one machine


from asmLexer import Lexer
from asmParser import Parser


def load(factory, fp):
	'''Load an assembly file into a low-level IR aterm.'''
	
	lexer = Lexer(fp)
	parser = Parser(lexer, factory = factory)
	term = parser.start()
	return term


def translate(term):
	'''Translate the "Asm" terms into the higher-level IR equivalent 
	constructs by means of the SSL.'''
	
	# FIXME: implement this
	
	return term
