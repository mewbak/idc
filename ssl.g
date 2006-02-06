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
    ast = parser.getAST()
    print ast
}

header "sslTreeParser.__main__" {
    from sslLexer import Lexer
    from sslParser import Parser
    
    lexer = Lexer()
    parser = Parser(lexer)
    parser.start()
    walker = Walker()
    ast = parser.getAST()
    print ast
    walker.start(ast)
    
    /*
    for n, (p, b) in walker.functions.iteritems():
        print "%s(%s) %s" % (n, ','.join(p), b.toStringList())
    */
    for n, (p, b) in walker.instructions.iteritems():
        print "%s(%s) %s" % (n, ','.join(p), b.toStringList())
}

header "sslTreeParser.__init__" {
    self.constants = {}
    self.tables = {}
    self.functions = {}
    self.instructions = {}
    self.locals = [{}]
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
XOR
	: '^'
		( ('"' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z')* '"') => '"'! ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z')* '"'! { $setType(DECOR); }
		| )
	;
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
	SPEC;
	CONSTANT;
	TABLE;
	CROSSP;
	FUNCTION;
	INSTR;
	INSTR_NAME;
	PARAMS;
	RTL;
}

start: specification EOF!;

specification
	: ( part SEMI! )*
		{ ## = #(#[SPEC,"SPEC"], ##) }
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

constant_def
	: NAME EQUATE! v:constant_expr
		{ ## = #(#[CONSTANT,"CONSTANT"], ##) }
	;

constant_expr
	: NUM ((PLUS^|MINUS^) NUM)*
	;

operands_decl!
	: "OPERAND" operand_decl ( COMMA operand_decl )*
	;

operand_decl
	: NAME EQUATE LCURLY parameter_list RCURLY
	| NAME parameter_list (LSQUARE parameter_list RSQUARE)? ASSIGNSIZE exp
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

registers_decl!
	: ("INTEGER"^| "FLOAT"^) register_decl (COMMA register_decl)*
	;

register_decl!
	: REG_ID INDEX num
	| REG_ID LSQUARE num RSQUARE INDEX num 
		( "COVERS" REG_ID TO REG_ID
		| "SHARES" REG_ID AT LSQUARE num TO num RSQUARE
		)?
	| LSQUARE! register_list RSQUARE! LSQUARE num RSQUARE INDEX num (TO num)?
	;

register_list
	: REG_ID (COMMA! REG_ID)*
	;

flag_func
	: NAME LPAREN! parameter_list RPAREN! LCURLY! rt_list RCURLY!
		{ ## = #(#[FUNCTION,"FUNCTION"], ##) }
	;

table_def
	: NAME EQUATE! table_expr
		{ ## = #(#[TABLE,"TABLE"], ##) }
	;

table_expr
	: (str_table) => str_table
	| opstr_table
	| exprstr_table
	;

str_table
	: primary_str_table (primary_str_table
		{ ## = #(#[CROSSP,"CROSSP"], ##) }
	  )*
	;

primary_str_table
	: NAME
	| LCURLY^ str_term (COMMA! str_term)* RCURLY!
	;

str_term
	: NAME
	| QUOTE QUOTE! { ## = #(##, #[NAME,""]) }
	| QUOTE^ NAME QUOTE!
	;

opstr_table 
	: LCURLY^ opstr_term (COMMA! t:opstr_term)* RCURLY!
	;

opstr_term
	: QUOTE^ bin_oper QUOTE!
	;

bin_oper
	: MOD | MUL | DIV | SMUL | SDIV | SMOD | PLUS | MINUS 
	| "rlc" | "rrc" | "rl" | "rr" | RSHIFT | LSHIFT | RSHIFTA | OR | ORNOT | AND | ANDNOT | XOR | XORNOT
	| MUL_F | MUL_FD | MUL_FQ | MUL_FSD | MUL_FDQ | DIV_F | DIV_FD | DIV_FQ | PLUS_F | PLUS_FD | PLUS_FQ | MINUS_F | MINUS_FD | MINUS_FQ | "pow"
	;

exprstr_table
	: LCURLY^ exprstr_term (COMMA! t:exprstr_term)* RCURLY!
	;

exprstr_term
	: QUOTE^ exp QUOTE!
	;

instr
	: instr_name parameter_list rt_list
		{ ## = #(#[INSTR,"INSTR"], ##) }
	;

instr_name
	: instr_name_head instr_name_tail (instr_name_decor)*
		{ ## = #(#[INSTR_NAME,"INSTR_NAME"], ##) }
	;

instr_name_head
	: (instr_name_elem) => instr_name_elem instr_name_tail
	| NAME^
	;

instr_name_elem
	: PRIME^ NAME PRIME!
	| QUOTE! NAME^ QUOTE!
	| NAME LSQUARE^ (num|NAME) RSQUARE!
	| DOLLAR! NAME LSQUARE^ (num|NAME) RSQUARE!
	;

instr_name_tail
	: (instr_name_elem) => instr_name_elem instr_name_tail
	| 
	;

instr_name_decor
	: DECOR^
	;

rt_list
	: (rt)+
		{ ## = #(#[RTL,"RTL"], ##) }
	;

rt
	: assign_rt
	| NAME LPAREN^ exp_list RPAREN!
//	| FLAGMACRO LPAREN (REG_ID ( COMMA! REG_ID)* )? RPAREN
	| UNDERSCORE^
	;

parameter_list
	: ((NAME) => NAME (COMMA! t:NAME)* | )
		{ ## = #(#[PARAMS,"PARAMS"], ##) }
	;

exp_list: (exp (COMMA! exp)* )?;

assign_rt
	: ASSIGNSIZE^ variable EQUATE! exp
/*		( (exp THEN) => exp THEN variable EQUATE exp
		| (exp) => exp
		| variable EQUATE exp
		)*/
	| "FPUSH"^
	| "FPOP"^
	;

primary_expr
	: NUM^
	| FLOATNUM^
//	| TEMP
	| REG_ID^
	| "r"^ LSQUARE! exp RSQUARE!
	| "m"^ LSQUARE! exp RSQUARE!
	| NAME^
	| LPAREN! exp RPAREN!
	| LSQUARE! exp QUEST^ exp COLON! exp RSQUARE!
	| "addr" LPAREN^ exp RPAREN!
//	| conv_func LPAREN num COMMA num COMMA exp RPAREN
//	| transcend LPAREN exp RPAREN
	| NAME LPAREN^ exp_list RPAREN!
	| NAME LSQUARE^ NAME RSQUARE!
	;

// bit extraction, sign extension, cast
postfix_expr
	: primary_expr 
		( (AT) => AT^ LSQUARE! exp COLON! exp RSQUARE!
		| (S_E) => S_E^
		| (LCURLY num RCURLY) => LCURLY^ num RCURLY!
		)*
	;

// operator lookup
lookup_expr
	: postfix_expr 
		( (NAME LSQUARE NAME RSQUARE) => NAME LSQUARE! NAME RSQUARE^ lookup_expr
		|
		)
	;

// not
unary_expr
	: (NOT^ | FNEG^ | LNOT^)* lookup_expr
	;
	
// floating point arithmetic
fp_expr
	: unary_expr ((MUL_F^ | MUL_FD^ | MUL_FQ^ | MUL_FSD^ | MUL_FDQ^ | DIV_F^ | DIV_FD^ | DIV_FQ^ | PLUS_F^ | PLUS_FD^ | PLUS_FQ^ | MINUS_F^ | MINUS_FD^ | MINUS_FQ^ | "pow"^) unary_expr)*
	;

// arithmetic
arith_expr
	: fp_expr ((MOD^ | MUL^ | DIV^ | SMUL^ | SDIV^ | SMOD^ | PLUS^ | MINUS^) fp_expr)*
	;

// bit arithmetic
bit_expr
	: arith_expr (("rlc"^ | "rrc"^ | "rl"^ | "rr"^ | RSHIFT^ | LSHIFT^ | RSHIFTA^ | OR^ | ORNOT^ | AND^ | ANDNOT^ | XOR^ | XORNOT^) arith_expr)*
	;

// conditionals
cond_expr
	: bit_expr ((EQ^ | NE^ | LT^ | GT^ | LE^ | GE^ | LTU^ | GTU^ | LEU^ | GEU^) bit_expr)*
	;
	
// logicals
log_expr
	: cond_expr (("and"^ | "or"^) cond_expr)*
	;

exp: log_expr;


variable
	: 
		( REG_ID^
		| "r"^ LSQUARE! exp RSQUARE!
		| "m"^ LSQUARE! exp RSQUARE!
		| NAME^
		) 
		( AT^ LSQUARE! exp COLON! exp RSQUARE! )*
	;

value
	: (PRIME^)? variable;

endianness: "ENDIANNESS" ( "BIG" | "LITTLE" );

fastlist: "FAST" fastentry (COMMA fastentry)*;

fastentry: NAME INDEX NAME;


class sslTreeParser extends TreeParser;
options {
	buildAST = true;
}

start!
	: #(SPEC (part)*)
	;

part!
	: #(CONSTANT cn:NAME cv=constant_expr)
		{ self.constants[cn.getText()] = #[NUM, str(cv)] }
	| #(TABLE tn:NAME tv=table_expr)
		{ self.tables[tn.getText()] = tv /* ; print tn.getText() + ": " + ", ".join([tvi.toStringList() for tvi in tv]) */ }
	| #(FUNCTION fn:NAME fp=parameter_list fb:RTL)
		{ self.functions[fn.getText()] = fp, self.astFactory.dupTree(fb) }
	| #(INSTR inam=instr_name ip=parameter_list ib:RTL)
		{
            for n, v in inam:
                self.locals.append(v)
                //print "Before: ", ib.toStringTree()
                self.rtl_subst(self.astFactory.dupTree(ib))
                //print "After :", self.returnAST
                rtl = self.returnAST
                //print
                self.locals.pop()
                
                if n in self.instructions:
                    old_ip, old_rtl = self.instructions[n]
                    assert ip == old_ip
                    old_rtl.addChild(rtl)
                else:
                    self.instructions[n] = ip, rtl
        }
	;

constant_expr! returns [res]
	: n:NUM
		{ res = int(n.getText()) }
	| #(PLUS x=constant_expr y=constant_expr)
		{ res = x + y }
	| #(MINUS x=constant_expr y=constant_expr)
		{ res = x - y }
	;

table_expr! returns [res]
	: #( LCURLY h=table_expr { res = h } (t=table_expr {res.extend(t)})* )
	| #( CROSSP h=table_expr { res = h } (t=table_expr {res = [self.astFactory.create(NAME, hh.getText() + tt.getText()) for tt in t for hh in h]})* )
	| #( QUOTE any:. ) { res = [self.astFactory.dupTree(any)] }
	| n:NAME { res = self.tables.get(n.getText(), [n]) }
	;

parameter_list! returns [res]
	: #(PARAMS { res = [] } (n:NAME { res.append(n.getText()) } )* )
	;
	
instr_name! returns [res]
	: #(INSTR_NAME {res = [("", {})] } (e=instr_name_elem {
        tmp = []
        for rn, rv in res:
            for en, ev in e:
                n = rn + en
                v = rv.copy()
                v.update(ev)
                tmp.append((n, v))
        res = tmp
	})*
	)
	;

instr_name_elem! returns [res]
	: n:NAME { res = [(n.getText(), {})] }
	| PRIME no:NAME { res = [("", {}), (no.getText(), {})] }
	| #(LSQUARE t1:NAME v:NAME) { res = [(self.tables[t1.getText()][idx].getText(), {v.getText(): self.astFactory.create(NUM, str(idx))}) for idx in range(len(self.tables[t1.getText()]))] }
	//| #(LSQUARE t2:NAME idx:NUM) { res = [(self.tables[t2.getText()][int(idx.getText())], {})] }
	| d:DECOR { res = [('.' + d.getText()[1:], {})] }
	;

rtl_subst
	: #(RTL (rtl_subst)*)
	|! n:NAME 
        {
            s = n.getText()
            if s in self.locals[-1]:
                ## = self.astFactory.dupTree(self.locals[-1][s])
            elif s in self.constants:
                ## = self.astFactory.dupTree(self.constants[s])
            else:
                ## = #(#n)
        }
    |! #(RSQUARE lexpr:rtl_subst t:NAME i:rtl_subst rexpr:rtl_subst)
        {
            if #i.getType() == NUM:
                op = self.astFactory.dup(self.tables[t.getText()][int(#i.getText())])
                ## = #(#op, #lexpr, #rexpr)
            else:
                ## = #(RSQUARE, #lexpr, #t, #i, #rexpr)
        }
    |! #(LPAREN f:NAME { args = [] } (a:rtl_subst { args.append(a) } )* )
        {
            if f.getText() in self.functions:
                params, rtl = self.functions[f.getText()]
                self.locals.append(dict(zip(params, args)))
                self.rtl_subst(rtl)
                ## = self.returnAST
                self.locals.pop()
            else:
                pass
        }
	|! #(r:. {/*print "=>", #r; */## = self.astFactory.dup(#r)} (no:rtl_subst { ##.addChild(#no) } )* )
	;

