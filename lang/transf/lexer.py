"""Custom transformation lexer."""


import antlr
import antlrre

from lang.transf import parser


pystr = \
	r"'''(?:\\.|.)*?'''|" \
	r'"""(?:\\.|.)*?"""|' \
	r'"(?:\\.|.)*?"|' \
	r"'(?:\\.|.)*?'"

pycomm = \
	r'#[^\r\n]*'

pyobj = '`(?:' + pycomm + '|' + pystr + '|[^`]*)`'


_tokenizer = antlrre.Tokenizer(
	# Token regular expression table
	tokens = [
		# whitespace and comments
		(parser.SKIP, 
			r'[ \t\f\r\n]+|'
			r'#[^\r\n]*',
		False),
		
		# REAL
		(parser.REAL, r'-?(?:'
			r'(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|'
			r'[0-9]+[eE][-+]?[0-9]+'
		r')', False), 
		
		# INT
		(parser.INT, r'-?[0-9]+', False),
	
		# STR
		(parser.STR, r'"[^"\\]*(?:\\.[^"\\]*)*"', False), 
		
		# IDs
		(parser.ID, 
			r'_[a-zA-Z0-9_]+|'
			r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+',
		False), 
		(parser.UID, r'[A-Z][a-zA-Z0-9_]*', False), 
		(parser.LID, r'[a-z][a-zA-Z0-9_]*', True), 

		(parser.RARROW, r'->', False),
		(parser.RDARROW, r'=>', False),
		
		(parser.OBJ, pyobj, False),
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
		'<': parser.LANGLE,
		'>': parser.RANGLE,
		',': parser.COMMA,
		':': parser.COLON,
		';': parser.SEMI,
		'*': parser.STAR,

		'\\': parser.RSLASH,
		'/': parser.LSLASH,
		
		'?': parser.QUEST,
		'!': parser.BANG,
		'+': parser.PLUS,
		#'-': parser.MINUS,
		'^': parser.CARET,
		'|': parser.VERT,
		'~': parser.TILDE,
		"'": parser.PRIME,
		'@': parser.AT,
		'=': parser.EQUAL,
	},
	
	# literals table
	literals = {
		"id": parser.IDENT,
		"fail": parser.FAIL,
		"if": parser.IF,
		"then": parser.THEN,
		"elif": parser.ELIF,
		"else": parser.ELSE,
		"end": parser.END,
		"let": parser.LET,
		"in": parser.IN,
		"where": parser.WHERE,
		"with": parser.WITH,
		"rec": parser.REC,
		"switch": parser.SWITCH,
		"case": parser.CASE,
	}
)


class Lexer(antlrre.TokenStream):

	tokenizer = _tokenizer
	
	def filterToken(self, type, text, pos, endpos):
		if False and type != antlr.SKIP:
			print parser._tokenNames[type], text
		if type == parser.SKIP:
			self.countLines(pos, endpos)
		elif type == parser.STR:
			self.countLines(pos, endpos)
			text = text[1:-1]
			text = text.replace('\\r', '\r')
			text = text.replace('\\n', '\n')
			text = text.replace('\\t', '\t')
			text = text.replace('\\', '')
		elif type == parser.OBJ:
			self.countLines(pos, endpos)
			text = text[1:-1]
		return type, text
