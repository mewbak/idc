// ANTLR grammar for the Semantics Specification Language (SSL)
//
// Based on:
// - citeseer.ist.psu.edu/cifuentes98specifying.html
// - sslscanner.l and sslparser.y from UQBT source distribution.

header {
}

header "sslParser.__main__" {
    from sslLexer import Lexer
    
    lexer = Lexer()
    parser = Parser(lexer)
    parser.start()
    print parser.getAST()
}

header "sslParser.__init__" {
}

options {
    language  = "Python";
}

class sslLexer extends Lexer;
options {
	k = 5;
	testLiterals=true;
}

tokens {
	WS;
	INTEGER = "INTEGER";
	FLOAT = "FLOAT";
	OPERAND = "OPERAND";
	FAST = "FAST";
	FETCHEXEC = "FETCHEXEC";
}

// Whitespace -- ignored
WS	: (' '|'\t'|'\f')+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n') { $newline; $setType(SKIP); }
	;

// Single-line comments
SL_COMMENT
	:	"#"
		(~('\n'|'\r'))* ('\n'|'\r'('\n')?)?
		{ $newline; $setType(SKIP); }
	;

protected
NUM	: ('-')? ('0'..'9')+
	| "0x" ('0'..'9'|'A'..'F')+ ;

protected
FLOATNUM : NUM '.' ('0'..'9')+ ( ('e'|'E') NUM )?;

FLOAT_OR_NUM
	: (FLOATNUM ) => FLOATNUM { $setType(FLOATNUM); }
	| (NUM) => NUM                     { $setType(NUM); }
	| (MINUS) => MINUS { $setType(MINUS); }
	;

NAME: ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9'|'_')*;

REG_ID:  '%' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9')*;

DECOR
	: '.' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'.'|'0'..'9')*
	//| '^' '"' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z') '"'
	;

COLON: ':';
EQUATE: ":=";
ASSIGN: "::=";
SEMI: ';';

COMMA	: ',';

LPAREN	: '(';
RPAREN	: ')';
LSQUARE	: '[';
RSQUARE	: ']';
LCURLY	: '{';
RCURLY	: '}';

INDEX : "->";
THEN : "=>";
TO	: "..";
AT : '@';
ASSIGNSIZE: '*' ('0'..'9')+ '*';

PRIME : '\'';

NOT: '~';
OR: '|';
AND: '&';
XOR: '^';
ORNOT: "|~";
ANDNOT: "&~";
XORNOT: "^~";

PLUS: '+';
protected
MINUS: '-';
MUL: '*';
DIV: '/';
MOD: '%';
SMUL: "*!";
SDIV: "/!";
SMOD: "%!";

EQ: '=';
LT: '<';
GT: '>';
NE: "~=";
LE: "<=";
GE: ">=";

LSHIFT: "<<";
RSHIFTA: ">>A";
RSHIFT: ">>";

MUL_F: "*f";
MUL_FD: "*fd";
MUL_FQ: "*fq";
MUL_FSD: "*fsd";
MUL_FDQ: "*fdq";
DIV_F: "/f";
DIV_FD: "/fd";
DIV_FQ: "/fq";
PLUS_F: "+f";
PLUS_FD: "+fd";
PLUS_FQ: "+fq";
MINUS_F: "-f";
MINUS_FD: "-fd";
MINUS_FQ: "-fq";
	
QUEST: '?';
S_E: '!';

DOT: '.';
QUOTE: '"';

DOLLAR: '$';

UNDERSCORE: '_';

FNEG: "~f";
LNOT: "~L";

class sslParser extends Parser;
options {
	buildAST = true;
	k = 5;
}

start: specification EOF;

specification
	: ( parts SEMI )*
	;

parts
	: instr
	| "FETCHEXEC" rt_list
	| constants
	| table_assign
	| endianness
	| fastlist
	| reglist
//	| definition
	| flag_fnc
	| "OPERAND" operandlist
	;
	
operandlist
	: operand ( COMMA operand )*
	;

operand
	: NAME EQUATE LCURLY list_parameter RCURLY
	| NAME list_parameter func_parameter ASSIGNSIZE exp
	;
	
func_parameter
	: LSQUARE list_parameter RSQUARE
	|
	;

definition
	: internal_type NAME
	| NAME ASSIGN NUM
	| aliases
	;

internal_type
	: INFINITESTACK
	;
	
aliases
	: REG_ID THEN exp
	;

reglist
	: (INTEGER | FLOAT) a_reglist (COMMA a_reglist)*
	;

a_reglist
	: REG_ID INDEX NUM
	| REG_ID LSQUARE NUM RSQUARE INDEX NUM 
		(
		| "COVERS" REG_ID TO REG_ID
		| "SHARES" REG_ID AT LSQUARE NUM TO NUM RSQUARE
		)
	| LSQUARE reg_table RSQUARE LSQUARE NUM RSQUARE INDEX NUM (TO NUM)?
	;

reg_table
	: REG_ID (COMMA REG_ID)*
	;

flag_fnc
	: NAME LPAREN list_parameter RPAREN LCURLY rt_list RCURLY
	;

constants
	: NAME EQUATE NUM ( ARITH_OP NUM )?
	;

table_assign: NAME EQUATE (table_expr)+;

table_expr
	: NAME
	| LCURLY 
		( (str_list) => str_list
		| opstr_list
		| exprstr_list
		) RCURLY
	;

str_list
	: str_term (COMMA str_term)* 
	;

str_term
	: NAME
	| name_contract
	| QUOTE QUOTE
	;

name_contract
	: PRIME NAME PRIME
	| NAME LSQUARE (NUM|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (NUM|NAME) RSQUARE
	| QUOTE NAME QUOTE
	;
	
opstr_list
	: opstr_term (COMMA opstr_term)*
	;

opstr_term
	: QUOTE bin_oper QUOTE
	;

bin_oper: bit_op | arith_op | farith_op;

exprstr_list: exprstr_term (COMMA exprstr_term)*;

exprstr_term: QUOTE exp QUOTE;

instr: instr_name list_parameter rt_list;

instr_name: instr_elem (instr_decor)*;

instr_elem
	: (NAME
	| PRIME NAME PRIME
	| NAME LSQUARE (NUM|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (NUM|NAME) RSQUARE
	| QUOTE NAME QUOTE
	) 
	( PRIME NAME PRIME
	| (NAME LSQUARE) => NAME LSQUARE (NUM|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (NUM|NAME) RSQUARE
	| QUOTE NAME QUOTE
	)*
	;

instr_decor
	: DECOR // DOT (NAME | NUM)
	| XOR QUOTE NAME QUOTE
	;

rt_list: (rt)+;

rt
	: assign_rt
	| NAME LPAREN list_actualparameter RPAREN
//	| FLAGMACRO LPAREN flag_list RPAREN
	| UNDERSCORE
	;

flag_list
	: (REG_ID ( COMMA REG_ID)* )?;
	
list_parameter
	: (NAME) => NAME (COMMA NAME)*
	|
	;

list_actualparameter: (exp (COMMA exp)* )?;

assign_rt
	: ASSIGNSIZE variable EQUATE exp
/*		( (exp THEN) => exp THEN variable EQUATE exp
		| (exp) => exp
		| variable EQUATE exp
		)*/
	| "FPUSH"
	| "FPOP"
	;

primary_expr
	: NUM
	| FLOATNUM
//	| TEMP
	| REG_ID
	| "r" LSQUARE exp RSQUARE
	| "m" LSQUARE exp RSQUARE
	| NAME
	| LPAREN exp RPAREN
	| LSQUARE exp QUEST exp COLON exp RSQUARE
	| "addr" LPAREN exp RPAREN
//	| conv_func LPAREN NUM COMMA NUM COMMA exp RPAREN
//	| transcend LPAREN exp RPAREN
	| NAME LPAREN list_actualparameter RPAREN
	| NAME LSQUARE NAME RSQUARE
	;

// bit extraction
postfix_expr
	: primary_expr (postfix_suffix)*
	;

postfix_suffix
	: (AT) => AT LSQUARE exp COLON exp RSQUARE
	| (S_E) => S_E
	| (LCURLY NUM RCURLY) => LCURLY NUM RCURLY
	;

lookup_expr
	: postfix_expr (
		(lookup_op) => lookup_op lookup_expr
		| )
	;

lookup_op
	: NAME LSQUARE! NAME RSQUARE!
	;

// sign extension

// 

// cast

// not
unary_expr
	: (NOT^ | FNEG^ | LNOT^)* lookup_expr
	;
	
// floating point arithmetic
expr5
	: unary_expr (farith_op unary_expr)*
	;

// arithmetic
expr6
	: expr5 (arith_op expr5)*
	;

// bit arithmetic
expr7
	: expr6 (bit_op expr6)*
	;

// conditionals
expr8
	: expr7 (cond_op expr7)*
	;
	
// logicals
expr9
	: expr8 (log_op expr8)*
	;

exp: expr9;


arith_op
	: MOD
	| MUL
	| DIV
	| SMUL
	| SDIV
	| SMOD
	| PLUS
	| MINUS
	;
	
bit_op
	: "rlc"
	| "rrc"
	| "rl"
	| "rr"
	| RSHIFT
	| LSHIFT
	| RSHIFTA
	| OR
	| ORNOT
	| AND
	| ANDNOT
	| XOR
	| XORNOT
	;

cond_op
	: EQ
	| NE
	| LT
	| GT
	| LE
	| GE
	| "<u"
	| ">u"
	| "<=u"
	| ">=u"
	;

farith_op
	: MUL_F
	| MUL_FD
	| MUL_FQ
	| MUL_FSD
	| MUL_FDQ
	| DIV_F
	| DIV_FD
	| DIV_FQ
	| PLUS_F
	| PLUS_FD
	| PLUS_FQ
	| MINUS_F
	| MINUS_FD
	| MINUS_FQ
	| "pow"
	;

log_op
	: "and"
	| "or"
	;

variable
	: (REG_ID
	| "r" LSQUARE exp RSQUARE
	| "m" LSQUARE exp RSQUARE
	| NAME )(AT LSQUARE exp COLON exp RSQUARE)*
	;

value
	: (PRIME)? variable;

endianness: "ENDIANNESS" ( "BIG" | "LITTLE" );

fastlist: "FAST" fastentry (COMMA fastentry)*;

fastentry: NAME INDEX NAME;


