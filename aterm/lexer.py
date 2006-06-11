"""Custom aterm lexer."""


import antlr
import re


# Tokens
INT=4
REAL=5
STR=6
CHAR=7
CONS=8
VAR=9
WILDCARD=10
LPAREN=11
RPAREN=12
LSQUARE=13
RSQUARE=14
COMMA=15
STAR=16
LCURLY=17
RCURLY=18
ASSIGN=19


# Token regular expressions 
# NOTE: order matters
tokens_re = [
	# whitespace
	r'[ |\t|\f]+',
	
	# newline
	r'\r\n?|\n',
	
	# REAL
	r'-?(?:'
		r'(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|'
		r'[0-9]+[eE][-+]?[0-9]+'
	r')', 
	
	# INT
	r'-?[0-9]+',

	# STR
	r'"[^"\\]*(?:\\.[^"\\]*)*"', 
	
	# CONS
	r'[A-Z][a-zA-Z0-9_]*', 
	
	# VAR
	r'[a-z][a-zA-Z0-9_]*' 
]
tokens_re = '|'.join(['(' + token_re + ')' for token_re in tokens_re])
tokens_re = re.compile(tokens_re, re.DOTALL)


group_table = [
	REAL,
	INT,
	STR,
	CONS,
	VAR,
]


char_table = {
	'_': WILDCARD,
	'(': LPAREN,
	')': RPAREN,
	'[': LSQUARE,
	']': RSQUARE,
	'{': LCURLY,
	'}': RCURLY,
	',': COMMA,
	'*': STAR,
	'=': ASSIGN,
}


class RecognitionException(antlr.RecognitionException):
	
	def __init__(self, *args):
		antlr.RecognitionException.__init__(self, *args)
		self.msg = args[0]
	
	def __str__(self):
		buf = antlr.RecognitionException.__str__(self)
		buf += self.msg
		return buf
	
	__repr__ = __str__
		

class Lexer(antlr.TokenStream):
	
	def __init__(self, buf, pos = 0, filename = None):
		self.buf = buf
		self.pos = pos
		self.line = 0
		self.linepos = pos
		self.filename = filename
	
	def nextToken(self):
		while True:
			# save state
			pos = self.pos
			line = self.line
			col = self.pos - self.linepos
			
			if self.pos == len(self.buf):
				type = antlr.EOF
				text = ""
				break
			mo = tokens_re.match(self.buf, pos)
			if mo:
				i = mo.lastindex
				self.pos = mo.end()
				if i == 1:
					# whitespace
					continue
				if i == 2:
					# newline
					self.line += 1
					self.linepos = self.pos
					continue
				text = mo.group()
				type = group_table[i - 3]
				if type == STR:
					lineoff = max(text.rfind('\r'), text.rfind('\n'))
					if lineoff != -1:
						self.linepos = pos + lineoff + 1
					text = text[1:-1]
					text = text.replace('\\r', '\r')
					text = text.replace('\\n', '\n')
					text = text.replace('\\t', '\t')
					text = text.replace('\\', '')
				break
			else:
				text = self.buf[pos]
				self.pos += 1
				try:
					type = char_table[text]
				except KeyError:
					msg = 'unexpected char: '
					if text >= ' ' and text <= '~':
						msg += "'%s'" % text
					else:
						msg += "0x%X" % text
					ex = RecognitionException(msg, self.filename, line, col)
					raise antlr.TokenStreamRecognitionException(ex)
				break
		return antlr.CommonToken(
			type = type, 
			text = text, 
			line = line, 
			col = col
		)

