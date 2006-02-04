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
    def p(t):
        for n,v in t.iteritems():
            print n
            print "", v
            print
    p(parser.constants)
    p(parser.tables)
    p(parser.functions)
    p(parser.instructions)
}

header "sslParser.__init__" {
    self.constants = {}
    self.tables = {}
    self.functions = {}
    self.instructions = {}
}

options {
    language  = "Python";
}


class sslLexer extends Lexer;
options {
	k = 4;
	testLiterals=true;
}

tokens {
	WS;
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
NUM	:
	(
		(   { s = 1 }
		|'-'! { s = -1 }
		)
		( ('0'..'9')+ { v = int($getText) }
		| "0x"! ('0'..'9'|'A'..'F')+ { v = int($getText, 16) }
		| "2**"! ('0'..'9')+ { v = 2**int($getText) }
		)
	) { v = str(v*s); $setText(v) }
	;

protected
FLOATNUM :  ('-')? ('0'..'9')+ '.' ('0'..'9')+ ( ('e'|'E') NUM )?;

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
NE: "~=";
LT: '<';
GT: '>';
LE: "<=";
GE: ">=";
LTU: "<u";
GTU: ">u";
LEU: "<=u";
GEU: ">=u";

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

tokens {
	CONSTANT_DEF;
	TABLE_DEF;
}

start: specification EOF;

specification
	: ( part SEMI! )*
	;

part
	: constant_def
	| registers_decl
	| operands_decl
	| flag_func
	| table_def
	| endianness
	| instr
	| fastlist
//	| definition
	;

num: NUM;

constant_def!
	: name:NAME EQUATE! value=constant_expr
		{ self.constants[name.getText()] = value }
	;

constant returns [res]
	: n:NUM { res = int(n.getText()) }
	;

constant_expr returns [res]
	: x=constant { res = x }
	| x=constant PLUS y=constant { res = x + y }
	| x=constant MINUS y=constant { res = x - y }
	;

operands_decl
	: "OPERAND" operand_decl ( COMMA operand_decl )*
	;

operand_decl
	: NAME EQUATE LCURLY parameter_list RCURLY
	| NAME parameter_list func_parameter ASSIGNSIZE exp
	;
	
func_parameter
	: LSQUARE parameter_list RSQUARE
	|
	;

definition
	: internal_type NAME
	| NAME ASSIGN num
	| aliases
	;

internal_type
	: INFINITESTACK
	;
	
aliases
	: REG_ID THEN exp
	;

registers_decl
	: register_type register_decl (COMMA register_decl)*
	;

register_type
	: "INTEGER"
	| "FLOAT"
	;

register_decl
	: REG_ID INDEX num
	| REG_ID LSQUARE num RSQUARE INDEX num 
		( "COVERS" REG_ID TO REG_ID
		| "SHARES" REG_ID AT LSQUARE num TO num RSQUARE
		)?
	| LSQUARE! register_list RSQUARE! LSQUARE num RSQUARE INDEX num (TO num)?
	;

register_list
	: REG_ID (COMMA REG_ID)*
	;

flag_func!
	: NAME LPAREN! parameter_list RPAREN! LCURLY! rt_list RCURLY!
	;

table_def!
	: n:NAME EQUATE! t=table
		{
            self.tables[n.getText()] = t
        }
	;

table returns [res]
	: (str_table) => t=str_table { res = t }
	| t=opstr_table { res = t }
	| t=exprstr_table { res = t }
	;


str_table returns [res]
	: t1=primary_str_table 
		{
            res = t1
		}	
	( t2=primary_str_table
		{
            tmp = []
            for i1 in res:
                for i2 in t2:
                  tmp.append(i1 + i2)
            res = tmp
		}
	)*
	;

primary_str_table returns [res]
	: n:NAME
		{ 
            try:
                res = self.tables[n.getText()]
            except KeyError:
                res = [n.getText()]
        }
	| LCURLY! x=str_term { res = x} (COMMA y=str_term { res.extend(y) } )* RCURLY!
	;

str_term returns [res]
	: n:NAME
		{ 
            try:
                res = self.tables[n.getText()]
            except KeyError:
                res = [n.getText()]
        }
	| QUOTE QUOTE { res = [""] }
	| QUOTE s:NAME QUOTE { res = [s.getText()] }
	;

name_contract
	: PRIME NAME PRIME
	| NAME LSQUARE (num|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (num|NAME) RSQUARE
	| QUOTE NAME QUOTE
	;

opstr_table returns [res]
	: LCURLY! h:opstr_term { res = [#h] } (COMMA t:opstr_term { res.append(#t) })* RCURLY!
	;

opstr_term
	: QUOTE! bin_oper QUOTE!
	;

bin_oper: bit_op | arith_op | farith_op;

exprstr_table returns [res]
	: LCURLY! h:exprstr_term { res = [#h] } (COMMA t:exprstr_term { res.append(#t) })* RCURLY!
	;

exprstr_term
	: QUOTE! exp QUOTE!
	;

instr: instr_name parameter_list rt_list;

instr_name: instr_elem (instr_decor)*;

instr_elem
	: (NAME
	| PRIME NAME PRIME
	| NAME LSQUARE (num|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (num|NAME) RSQUARE
	| QUOTE NAME QUOTE
	) 
	( PRIME NAME PRIME
	| (NAME LSQUARE) => NAME LSQUARE (num|NAME) RSQUARE
	| DOLLAR NAME LSQUARE (num|NAME) RSQUARE
	| QUOTE NAME QUOTE
	)*
	;

instr_decor
	: DECOR // DOT (NAME | num)
	| XOR QUOTE NAME QUOTE
	;

rt_list: (rt)+;

rt
	: assign_rt
	| NAME LPAREN exp_list RPAREN
//	| FLAGMACRO LPAREN flag_list RPAREN
	| UNDERSCORE
	;

flag_list
	: (REG_ID ( COMMA REG_ID)* )?;
	
parameter_list
	: (NAME) => NAME (COMMA NAME)*
	|
	;

exp_list: (exp (COMMA exp)* )?;

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
	: num
	| FLOATNUM
//	| TEMP
	| REG_ID
	| "r" LSQUARE exp RSQUARE
	| "m" LSQUARE exp RSQUARE
	| NAME
	| LPAREN exp RPAREN
	| LSQUARE exp QUEST exp COLON exp RSQUARE
	| "addr" LPAREN exp RPAREN
//	| conv_func LPAREN num COMMA num COMMA exp RPAREN
//	| transcend LPAREN exp RPAREN
	| NAME LPAREN exp_list RPAREN
	| NAME LSQUARE NAME RSQUARE
	;

// bit extraction
postfix_expr
	: primary_expr (postfix_suffix)*
	;

postfix_suffix
	: (AT) => AT LSQUARE exp COLON exp RSQUARE
	| (S_E) => S_E
	| (LCURLY num RCURLY) => LCURLY num RCURLY
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
fp_expr
	: unary_expr (farith_op unary_expr)*
	;

// arithmetic
arith_expr
	: fp_expr (arith_op fp_expr)*
	;

// bit arithmetic
bit_expr
	: arith_expr (bit_op arith_expr)*
	;

// conditionals
cond_expr
	: bit_expr (cond_op bit_expr)*
	;
	
// logicals
log_expr
	: cond_expr (log_op cond_expr)*
	;

exp: log_expr;


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
	| LTU
	| GTU
	| LEU
	| GEU
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

