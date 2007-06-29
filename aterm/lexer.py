"""Term textual representation tokenization."""


import os.path
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
			if test_lit:
				type = self.literals_table.get(text, type)
			return type, text, pos
		else:
			c = buf[pos]
			return self.symbols_table.get(c, None), c, pos + 1


class TokenStream(antlr.TokenStream):

	tokenizer = None

	newline_re = re.compile(r'\r\n?|\n')

	tabsize = 8

	def __init__(self, buf = None, pos = 0, filename = None, fp = None):
		if fp is not None:
			try:
				fileno = fp.fileno()
				length = os.path.getsize(fp.name)
				import mmap
			except:
				# read whole file into memory
				buf = fp.read()
				pos = 0
			else:
				# map the whole file into memory
				if length:
					# length must not be zero
					buf = mmap.mmap(fileno, length, access = mmap.ACCESS_READ)
					pos = os.lseek(fileno, 0, 1)
				else:
					buf = ""
					pos = 0

			if filename is None:
				try:
					filename = fp.name
				except AttributeError:
					filename = None

		self.buf = buf
		self.pos = pos
		self.line = 1
		self.col = 1
		self.filename = filename

	def nextToken(self):
		while True:
			# save state
			pos = self.pos
			line = self.line
			col = self.col

			type, text, endpos = self.tokenizer.next(self.buf, pos)
			self.consume(text)
			type, text = self.filterToken(type, text)
			self.pos = endpos

			if type == antlr.SKIP:
				continue
			elif type is None:
				msg = 'unexpected token: '
				if text >= ' ' and text <= '~':
					msg += "'%s'" % text
				else:
					msg += "0x%X" % ord(text)
				ex = antlr.RecognitionException(msg, self.filename, line, col)
				raise ex
				#raise antlr.TokenStreamRecognitionException(ex)
			else:
				break
		return (type, text, line, col)

	def consume(self, text):
		# update line number
		pos = 0
		for mo in self.newline_re.finditer(text, pos):
			self.line += 1
			self.col = 1
			pos = mo.end()

		# update column number
		while True:
			tabpos = text.find('\t', pos)
			if tabpos == -1:
				break
			self.col += tabpos - pos
			self.col = ((self.col - 1)//self.tabsize + 1)*self.tabsize + 1
			pos = tabpos + 1
		self.col += len(text) - pos

	def filterToken(self, type, text):
		return type, text


_tokenizer = Tokenizer(
	# Token regular expression table
	tokens = [
		# whitespace
		(parser.SKIP, r'[ \t\f\r\n]+', False),

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
	}
)


class Lexer(TokenStream):
	'''Lexer for scanning terms.'''

	tokenizer = _tokenizer

	def filterToken(self, type, text):
		if type == parser.STR:
			text = text[1:-1]
			text = text.replace('\\r', '\r')
			text = text.replace('\\n', '\n')
			text = text.replace('\\t', '\t')
			text = text.replace('\\', '')
		return type, text
