"""Custom transformation lexer."""


import antlr
import antlrre

from transf.parse import parser


#PYSTR
#	: "'''" ESC | EOL | .  "'''"
#	| '"""' ESC | EOL | .  '"""'
#	| "'" ( ESC | ~'\'' )* "'"
#	| '"' ( ESC | ~'"' )* '"'
#	;

#pycode = '`'! ( COMMENT | PYSTR | ~'`' )* '`'!


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

		(parser.APPLY_MATCH, r'=>', False),
		(parser.INTO, r'->', False)
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
		'-': parser.MINUS,
		'^': parser.CARET,
		'|': parser.VERT,
		'~': parser.TILDE,
		'@': parser.AT,
		'=': parser.EQUAL,

	},
	
	# literals table
	literals = {
		"id": parser.IDENT,
		"fail": parser.FAIL,
		"if": parser.IF,
		"then": parser.THEN,
		"else": parser.ELSE,
		"end": parser.END,
		"let": parser.LET,
		"in": parser.IN,
		"where": parser.WHERE,
		"rec": parser.REC,
		"switch": parser.SWITCH,
		"case": parser.CASE,
		"otherwise": parser.OTHERWISE,		
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
		return type, text