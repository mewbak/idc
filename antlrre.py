"""Support for custom antlr lexers using regular expressions."""


import os
import mmap
import re

import antlr


class Tokenizer(object):
	
	def __init__(self, tokens = (), symbols = None, literals = None):
		self.tokens_re = re.compile(
			'|'.join(['(' + regexp + ')' for tok, regexp, test_lit in tokens]), 
			re.DOTALL
		)
		self.tokens_table = tokens
		if symbols is None:
			self.symbols_table = {}
		else:
			self.symbols_table = symbols
		if literals is None:
			self.literals_table = {}
		else:
			self.literals_table = literals
	
	def next(self, buf, pos):
		if pos >= len(buf):
			return antlr.EOF, "", pos
		mo = self.tokens_re.match(buf, pos)
		if mo:
			text = mo.group()
			type, _, test_lit = self.tokens_table[mo.lastindex - 1]
			pos = mo.end()
			if test_lit:
				type = self.literals_table.get(text, type)
			return type, text, pos
		else:
			c = buf[pos]
			return self.symbols_table.get(c, None), c, pos + 1


class TokenStream(antlr.TokenStream):

	tokenizer = None
	
	newline_re = re.compile(r'\r\n?|\n')
	
	def __init__(self, buf = None, pos = 0, filename = None, fp = None):
		if fp is not None:
			try:
				fileno = fp.fileno()
			except AttributeError:
				# read whole file into memory
				buf = fp.read()
				pos = 0
			else:
				# map the whole file into memory
				curpos = os.lseek(fileno, 0, 0)
				length = os.lseek(fileno, 0, 2)
				os.lseek(fileno, curpos, 0)
				# length must not be zero
				if length:
					buf = mmap.mmap(fileno, length, access = mmap.ACCESS_READ)
				else:
					buf = ""
			
			if filename is None:
				try:
					filename = fp.name
				except AttributeError:
					filename = None

		self.buf = buf
		self.pos = pos
		self.lineno = 0
		self.linepos = pos
		self.filename = filename
	
	def nextToken(self):
		while True:
			# save state
			pos = self.pos
			line = self.lineno
			col = self.pos - self.linepos
			
			type, text, endpos = self.tokenizer.next(self.buf, pos)
			type, text = self.filterToken(type, text, pos, endpos)
			self.pos = endpos
			
			if type == antlr.SKIP:
				continue
			elif type is None:
				msg = 'unexpected token: '
				if text >= ' ' and text <= '~':
					msg += "'%s'" % text
				else:
					msg += "0x%X" % text
				ex = antlr.RecognitionException(msg, self.filename, line, col)
				raise antlr.TokenStreamRecognitionException(ex)
			else:
				break
		return antlr.CommonToken(
			type = type, 
			text = text, 
			line = line, 
			col = col
		)
		
	def filterToken(self, type, text, pos, endpos):
		return type, text

	def countLines(self, pos, endpos):
		for mo in self.newline_re.finditer(self.buf, pos, endpos):
			self.lineno += 1
			self.linepos = mo.endpos