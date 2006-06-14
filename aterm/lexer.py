"""Custom aterm lexer."""


import re

import antlr

from aterm import parser


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
			# TODO: test literals
			return type, text, pos
		else:
			c = buf[pos]
			return self.symbols_table.get(c, None), c, pos + 1


class Lexer(antlr.TokenStream):

	tokenizer = Tokenizer(
		# Token regular expression table
		tokens = [
			# whitespace
			(parser.SKIP, r'[ |\t|\f\r\n]+', False),
			
			# REAL
			(parser.REAL, r'-?(?:'
				r'(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|'
				r'[0-9]+[eE][-+]?[0-9]+'
			r')', False), 
			
			# INT
			(parser.INT, r'-?[0-9]+', False),
		
			# STR
			(parser.STR, r'"[^"\\]*(?:\\.[^"\\]*)*"', False), 
			
			# CONS
			(parser.CONS, r'[A-Z][a-zA-Z0-9_]*', False), 
			
			# VAR
			(parser.VAR, r'[a-z][a-zA-Z0-9_]*', False),
		],
		
		# symbols table
		symbols = {
			'_': parser.WILDCARD,
			'(': parser.LPAREN,
			')': parser.RPAREN,
			'[': parser.LSQUARE,
			']': parser.RSQUARE,
			'{': parser.LCURLY,
			'}': parser.RCURLY,
			',': parser.COMMA,
			'*': parser.STAR,
			'=': parser.ASSIGN,
		}
	)
	
	newline_re = re.compile(r'\r\n?|\n')
	
	def __init__(self, buf, pos = 0, filename = None):
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
			
			if type == parser.SKIP:
				continue
			elif type is None:
				msg = 'unexpected token: '
				if text >= ' ' and text <= '~':
					msg += "'%s'" % text
				else:
					msg += "0x%X" % text
				ex = RecognitionException(msg, self.filename, line, col)
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
		if type == parser.SKIP:
			self.countLines(pos, endpos)
		elif type == parser.STR:
			self.countLines(pos, endpos)
			text = text[1:-1]
			text = text.replace('\\r', '\r')
			text = text.replace('\\n', '\n')
			text = text.replace('\\t', '\t')
			text = text.replace('\\', '')
		return type, text

	def countLines(self, pos, endpos):
		for mo in self.newline_re.finditer(self.buf, pos, endpos):
			self.lineno += 1
			self.linepos = mo.endpos
