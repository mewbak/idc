"""Term textual representation tokenization."""


import antlrre

from aterm import parser


_tokenizer = antlrre.Tokenizer(
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


class Lexer(antlrre.TokenStream):
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
