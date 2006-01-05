header {
}

header "asmParser.__main__" {
// parser test program
	from asmLexer import Lexer
	
	lexer = Lexer()
	parser = Parser(lexer)
	parser.start()
	t = parser.getAST()
	print t
}

options {
    language  = "Python";
}

class asmLexer extends Lexer;
options {
	k = 2;
}

DIRECTIVE: '.' ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'0'..'9')*;

INSTRUCTION: ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'0'..'9')*;





BINARY: '0' ('b'|'B') ('0'|'1')*;
HEXADECIMAL: '0' ('x'|'X') ('0'..'9'|'a'..'f'|'A'..'F')*;
OCTAL: '0' ('0'..'9')*;
DECIMAL: '1'..'9' ('0'..'9')*;

// TODO: float point numbers

PERCENTAGE: '%';
DOLLAR: '$';
COMMA: ',';
COLON: ':';
AT: '@';

LPAR: '(';
RPAR: ')';


MINUS: '-';

PLUS: '+';

CHAR
	:	'\'' (ESC|~'\'') '\''
	;

STRING
	:	'"' (ESC|~'"')* '"'
	;

protected
ESC	:	'\\'
		(	'n'
		|	'r'
		|	't'
		|	'b'
		|	'f'
		|	'"'
		|	'\''
		|	'\\'
		|	'0'..'3'
			(
				options {
					warnWhenFollowAmbig = false;
				}
			:	'0'..'9'
				(
					options {
						warnWhenFollowAmbig = false;
					}
				:	'0'..'9'
				)?
			)?
		|	'4'..'7'
			(
				options {
					warnWhenFollowAmbig = false;
				}
			:	'0'..'9'
			)?
		)
	;


// Whitespace -- ignored
WS  :
        (   ' '
        |   '\t'
        |   '\f'
        )
        { _ttype = Token.SKIP; }
    ;

EOL
    :
        (   "\r\n"  // DOS
        |   '\r'    // Macintosh
        |   '\n'    // Unix
        )
        { self.newline(); }
    ;

// Single-line comments
SL_COMMENT
	:	"#"
		(~('\n'|'\r'))* ('\n'|'\r'('\n')?)?
		{$setType(Token.SKIP); newline();}
	;

// multiple-line comments
//ML_COMMENT
// 	:	"/*"
// 		(	
// 			{ LA(2)!='/' }? '*'
// 		|	'\r' '\n'		{newline();}
// 		|	'\r'			{newline();}
// 		|	'\n'			{newline();}
// 		|	~('*'|'\n'|'\r')
// 		)*
// 		"*/"
// 		{$setType(Token.SKIP);}
// 	;

class asmParser extends Parser;
options {
	buildAST=true;
	k = 3;
}

start: (statement)* EOF;

statement: labels tail EOL;

labels	: (symbol COLON) => (symbol COLON^ labels)
	| /* no label */
	;

tail	: /* empty statement */
	| DIRECTIVE^ (~EOL)*
	| prefixed_instruction
	;

prefixed_instruction
	: (instruction) => instruction
	| INSTRUCTION instruction
	;
instruction: INSTRUCTION^ (operand (COMMA! operand)* )?;
 
operand	: (memory) => memory
	| constant
	| immediate 
	| register 
	;

immediate: DOLLAR^ constant;

register: PERCENTAGE^ symbol;

memory: (disp:constant)? LPAR! (base:register)? (COMMA! (index:register)? (COMMA! (scale:integer)? )? )? RPAR!;

constant: symbol | integer;

symbol: DIRECTIVE | INSTRUCTION;

integer	: BINARY
	| OCTAL 
	| DECIMAL
	| HEXADECIMAL
	| MINUS^ integer
	;

