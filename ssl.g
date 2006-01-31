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

NAME: ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9')*;

REG_ID:  '%' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9')*;


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
RSHIFT: ">>";

QUEST: '?';
S_E: '!';

DOT: '.';
QUOTE: '"';

DOLLAR: '$';

UNDERSCORE: '_';

class sslParser extends Parser;
options {
	buildAST = true;
	k = 4;
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

table_assign: NAME EQUATE table_expr;

table_expr
	: (str_expr) => str_expr
	| opstr_expr
	| exprstr_expr
	;
	
str_expr
	: (str_term)*
	;

opstr_expr
	: LCURLY opstr (COMMA opstr)* RCURLY
	;

opstr
	: QUOTE ( bit_op | arith_op | farith_op ) QUOTE
	;
	
str_array
	: /* str_array str_expr
	| str_array COMMA QUOTE QUOTE
	| */ str_expr
	;

str_term
	: LCURLY str_array RCURLY
	| name_expand
	;

name_expand
	: "'" NAME "'"
	| QUOTE NAME QUOTE
	| DOLLAR NAME
	| NAME
	;
	
bin_oper: BIT_OP | ARITH_OP | FARITH_OP;

opstr_array: QUOTE bin_oper QUOTE (COMMA QUOTE bin_oper QUOTE)*;

exprstr_expr: LCURLY exprstr_array RCURLY;

exprstr_array: QUOTE exp QUOTE (COMMA QUOTE exp QUOTE)*;

instr: instr_name list_parameter rt_list;

instr_name: instr_elem (instr_decor)*;

instr_elem
	: n:NAME (LSQUARE (NUM | NAME) RSQUARE)?
	;

instr_decor
	: DOT NAME
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
//	| FPUSH
//	| FPOP
	;

expr0
	: NUM
	| FLOATNUM
//	| TEMP
	| value
	| LPAREN exp RPAREN
	| LSQUARE exp QUEST exp COLON exp RSQUARE
	| "addr" LPAREN exp RPAREN
//	| conv_func LPAREN NUM COMMA NUM COMMA exp RPAREN
//	| FPUSH
//	| FPOP
//	| transcend LPAREN exp RPAREN
	| NAME LPAREN list_actualparameter RPAREN
	;

// bit extraction
expr1
	: expr0 (AT LSQUARE exp COLON exp RSQUARE)?
	;

// sign extension
expr2
	: expr1 (S_E)*
	;

// 
expr23
	: expr2 ((NAME LSQUARE) => NAME LSQUARE NAME RSQUARE expr2 | )
	;

// cast
expr3
	: expr23 (LCURLY NUM RCURLY)?
	;

// not
expr4
	: (NOT)* expr3
	;
	
// floating point arithmetic
expr5
	: expr4 (farith_op expr4)*
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
	| ">>A"
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
	: "*f"
	| "*fd"
	| "*fq"
	| "*fsd"
	| "*fdq"
	| "/f"
	| "/fd"
	| "/fq"
	| "+f"
	| "+fd"
	| "+fq"
	| "-f"
	| "-fd"
	| "-fq"
	;

log_op
	: "and"
	| "or"
	;

variable
	: REG_ID
	| "r" LSQUARE exp RSQUARE
	| "m" LSQUARE exp RSQUARE
	| NAME
	;

value
	: (PRIME)? variable;

endianness: "ENDIANNESS" ( "BIG" | "LITTLE" );

fastlist: "FAST" fastentry (COMMA fastentry)*;

fastentry: NAME INDEX NAME;


