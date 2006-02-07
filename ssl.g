// ANTLR grammar for the Semantics Specification Language (SSL)
//
// Based on:
// - citeseer.ist.psu.edu/cifuentes98specifying.html
// - sslscanner.l and sslparser.y from UQBT source distribution.
// - sslscanner.l and sslparser.y from boomerang source distribution.

header {

import antlr

class SemanticException(antlr.SemanticException):

    def __init__(self, node, msg):
        antlr.SemanticException.__init__(self)
        self.node = node
        self.msg = msg

    def __str__(self):
        line = self.node.getLine()
        col  = self.node.getColumn()
        text = self.node.getText()
        return "line %s:%s: \"%s\": %s" % (line, col, text, self.msg)

    __repr__ = __str__

}

header "sslParser.__main__" {
    from sslLexer import Lexer
    
    lexer = Lexer()
    parser = Parser(lexer)
    parser.start()
    ast = parser.getAST()
    print ast
}

header "sslPreprocessor.__main__" {
    from sslLexer import Lexer
    from sslParser import Parser
    
    lexer = Lexer()
    parser = Parser(lexer)
    parser.start()
    walker = Walker()
    ast = parser.getAST()
    walker.start(ast)
    ast = walker.getAST()
    
    names = walker.instructions.keys()
    names.sort()
    for name in names:
        params, body = walker.instructions[name]
        print "%s(%s) %s" % (name, ','.join(params), body.toStringList())
}

header "sslPreprocessor.__init__" {
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

// Whitespace -- ignored
WS
	: (' '|'\t'|'\f')+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n') { $newline; $setType(SKIP); }
	;

// Single-line comments
COMMENT
	:	"#"
		(~('\n'|'\r'))* ('\n'|'\r'('\n')?)?
		{ $newline; $setType(SKIP); }
	;

protected
NUM	:
		( { s = 1 }
		|'-'! { s = -1 }
		)
		( ('0'..'9')+ { v = int($getText) }
		| "0x"! ('0'..'9'|'A'..'F')+ { v = int($getText, 16) }
		| "2**"! ('0'..'9')+ { v = 2**int($getText) }
		)
		{ v = str(v*s); $setText(v) }
	;

protected
FLOATNUM
	: ('-')? ('0'..'9')+ '.' ('0'..'9')+ ( ('e'|'E') NUM )?
	;

FLOAT_OR_NUM
	: (FLOATNUM ) => FLOATNUM { $setType(FLOATNUM); }
	| (NUM) => NUM                     { $setType(NUM); }
	| (MINUS) => MINUS { $setType(MINUS); }
	;

NAME
	: ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9'|'_')*
	;

REG_ID
	:  '%' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'0'..'9')*
	;

DECOR
	: '.' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z'|'.'|'0'..'9')*
	;

COLON: ':';
EQUATE: ":=";
ASSIGN: "::=";
SEMI: ';';

COMMA: ',';

LPAREN: '(';
RPAREN: ')';
LSQUARE: '[';
RSQUARE: ']';
LCURLY: '{';
RCURLY: '}';

INDEX: "->";
THEN: "=>";
TO: "..";
AT: '@';
ASSIGNTYPE: '*' /* ('a'..'z')?*/ ('0'..'9')* '*';

PRIME: '\'';

NOT: '~';
OR: '|';
AND: '&';
XOR
	: '^'
		( ('"' ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z')* '"') => 
			'"'! ('A'..'Z'|'a'..'z')('A'..'Z'|'a'..'z')* '"'! { $setType(DECOR); }
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
	k = 3;
}

tokens {
	SPEC;
	CONSTANT;
	TABLE;
	CROSSP;
	FUNCTION;
	INSTR;
	INSTR_NAME;
	LOOKUP_OP;
	PARAMS;
	BUILTIN;
	RTL;
}

start
	: specification EOF!
	;

specification
	: ( part SEMI! )*
		{ ## = #(#[SPEC,"SPEC"], ##) }
	;

part
	: constant_def
	| registers_decl
	| operands_decl
	| endianness
	| function_def
	| table_def
	| instr_def
	| fast_list
	;

num: NUM;

constant_def
	: NAME EQUATE! v:constant_expr
		{ ## = #(#[CONSTANT,"CONSTANT"], ##) }
	;

constant_expr
	: NUM ((PLUS^|MINUS^) NUM)*
	;

registers_decl
	: ("INTEGER"^| "FLOAT"^) register_decl (COMMA! register_decl)*
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
	: REG_ID (COMMA! REG_ID)*
	;

operands_decl
	: "OPERAND"^ operand_decl ( COMMA! operand_decl )*
	;

operand_decl
	: NAME^ EQUATE LCURLY! parameter_list RCURLY!
	| NAME^ parameter_list (LSQUARE parameter_list RSQUARE)? ASSIGNTYPE expr
	;

endianness: "ENDIANNESS"^ ( "BIG" | "LITTLE" );

function_def
	: NAME LPAREN! parameter_list RPAREN! LCURLY! rt_list RCURLY!
		{ ## = #(#[FUNCTION,"FUNCTION"], ##) }
	;

table_def
	: NAME EQUATE! table_expr
		{ ## = #(#[TABLE,"TABLE"], ##) }
	;

table_expr
	: (str_table_expr) => str_table_expr
	| opstr_table
	| exprstr_table
	;

str_table_expr
	: str_table (str_table
		{ ## = #(#[CROSSP,"CROSSP"], ##) }
	  )*
	;

str_table
	: NAME
	| LCURLY^ str_entry (COMMA! str_entry)* RCURLY!
	;

str_entry
	: NAME
	| QUOTE QUOTE! { ## = #(##, #[NAME,""]) }
	| QUOTE^ NAME QUOTE!
	;

opstr_table 
	: LCURLY^ opstr_entry (COMMA! t:opstr_entry)* RCURLY!
	;

opstr_entry
	: QUOTE^ bin_oper QUOTE!
	;

bin_oper
	: MOD | MUL | DIV | SMUL | SDIV | SMOD | PLUS | MINUS 
	| "rlc" | "rrc" | "rl" | "rr" | RSHIFT | LSHIFT | RSHIFTA | OR | ORNOT | AND | ANDNOT | XOR | XORNOT
	| MUL_F | MUL_FD | MUL_FQ | MUL_FSD | MUL_FDQ | DIV_F | DIV_FD | DIV_FQ | PLUS_F | PLUS_FD | PLUS_FQ | MINUS_F | MINUS_FD | MINUS_FQ | "pow"
	;

exprstr_table
	: LCURLY^ exprstr_entry (COMMA! t:exprstr_entry)* RCURLY!
	;

exprstr_entry
	: QUOTE^ expr QUOTE!
	;

instr_def
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

// register transfer list
rt_list
	: (rt)+
		{ ## = #(#[RTL,"RTL"], ##) }
	;

rt
	: assign_rt
	| NAME LPAREN! expr_list RPAREN! { ## = #(#[FUNCTION,"FUNCTION"], ##) }
	| ("undefineflags"^| "defineflags"^) LPAREN! (REG_ID ( COMMA! REG_ID)* )? RPAREN!
	| UNDERSCORE!
	;

parameter_list
	: ((NAME) => NAME (COMMA! t:NAME)* | )
		{ ## = #(#[PARAMS,"PARAMS"], ##) }
	;

assign_rt
	: ASSIGNTYPE^ variable EQUATE! expr
//	| ASSIGNTYPE^ expr THEN variable EQUATE! expr
//	| ASSIGNTYPE^ expr
	| "FPUSH"^
	| "FPOP"^
	;

variable
	: 
		( REG_ID^
		| "r"^ LSQUARE! expr RSQUARE!
		| "m"^ LSQUARE! expr RSQUARE!
		| NAME^
		) 
		( AT^ LSQUARE! expr COLON! expr RSQUARE! 
		| PRIME^
		)*
	;

primary_expr
	: NUM^
	| FLOATNUM^
//	| TEMP
	| REG_ID^
	| "r"^ LSQUARE! expr RSQUARE!
	| "m"^ LSQUARE! expr RSQUARE!
	| NAME^
	| NAME LSQUARE! (NAME|NUM) RSQUARE!	{ ## = #([TABLE,"TABLE"], ##) }
	| LPAREN! expr RPAREN!
	| LSQUARE! expr QUEST^ expr COLON! expr RSQUARE!
	| NAME LPAREN! expr_list RPAREN! { ## = #([BUILTIN,"BUILTIN"], ##) }
	;

// bit extraction, sign extension, cast
postfix_expr
	: primary_expr 
		( (AT) => AT^ LSQUARE! expr COLON! expr RSQUARE!
		| (S_E) => S_E^
		| (LCURLY num RCURLY) => LCURLY^ num RCURLY!
		)*
	;

// operator lookup
lookup_expr
	: postfix_expr 
		( (NAME LSQUARE NAME RSQUARE) => NAME LSQUARE! NAME RSQUARE! lookup_expr
			{ ## = #([LOOKUP_OP,"LOOKUP_OP"], ##) }
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

expr: log_expr;

expr_list: (expr (COMMA! expr)* )?;

fast_list: "FAST"^ fast_entry (COMMA! fast_entry)*;

fast_entry: NAME INDEX^ NAME;


// SSL AST preprocessor that replaces references to constants, tables, and 
// functions by their actual values.
class sslPreprocessor extends TreeParser;
options {
	buildAST = true;
}

start
	: #(SPEC (part)*)
		{
            // Rebuild the expanded instructions
            names = self.instructions.keys()
            names.sort()
            for name in names:
                params, body_ast = self.instructions[name]
                params_ast = #(#[PARAMS,"PARAMS"])
                for param in params:
                   params_ast.addChild(#(#[NAME,param]))
                instr_ast = #(#[INSTR,"INSTR"], #[NAME,name], params_ast, body_ast)
                ##.addChild(instr_ast)
		}
	;

part
	:! #(CONSTANT cn:NAME cv=constant_expr)
		{ self.constants[cn.getText()] = #[NUM, str(cv)] }
	|! #(TABLE tn:NAME tv=table_expr)
		{ self.tables[tn.getText()] = tv }
	|! #(FUNCTION fn:NAME fp=parameter_list fb:RTL)
		{ self.functions[fn.getText()] = fp, self.astFactory.dupTree(fb) }
	|! #(INSTR inam=instr_name ip=parameter_list ib:RTL)
		{
            for n, v in inam:
                self.locals.append(v)
                self.rtl_expand(self.astFactory.dupTree(ib))
                rtl = self.getAST()
                self.locals.pop()
                
                if n in self.instructions:
                    old_ip, old_rtl = self.instructions[n]
                    assert ip == old_ip
                    if rtl.getFirstChild():
	                    old_rtl.addChild(rtl.getFirstChild())
                else:
                    self.instructions[n] = ip, rtl
        }
	| #( . ( . )* )
		// copy other parts unmodified
	;

constant_expr! returns [v]
	: n:NUM
		{ v = int(n.getText()) }
	| #(PLUS l=constant_expr r=constant_expr)
		{ v = l + r }
	| #(MINUS l=constant_expr r=constant_expr)
		{ v = l - r }
	;

table_expr! returns [res]
	: #( LCURLY h=table_expr { res = h } (t=table_expr { res.extend(t) })* )
	| #( CROSSP h=table_expr { res = h } (t=table_expr { res = [self.astFactory.create(NAME, hh.getText() + tt.getText()) for tt in t for hh in h] })* )
	| #( QUOTE any:. ) { res = [self.astFactory.dupTree(any)] }
	| n:NAME { res = self.tables.get(n.getText(), [n]) }
	;

parameter_list! returns [res]
	: #(PARAMS { res = [] } ( n:NAME { res.append(n.getText()) } )* )
	;

// Returns a list of ('name', 'variables') pairs, where 'name' is the 
// instruction name and 'variables' is a dict mapping the corresponding 
// variables/values resulting from table lookup.
instr_name! returns [res]
	: #( INSTR_NAME 
			{ res = [("", {})] }
		( e=instr_name_elem
            {
                tmp = []
                for rn, rv in res:
                    for en, ev in e:
                        n = rn + en
                        v = rv.copy()
                        v.update(ev)
                        tmp.append((n, v))
                res = tmp
            }
		)*
	)
	;

// Same return value as 'instr_name'.
instr_name_elem! returns [res]
	: name:NAME
		{ res = [(#name.getText(), {})] }
	| PRIME optname:NAME 
		{ res = [("", {}), (#optname.getText(), {})] }
	| #(LSQUARE tname:NAME
		{
            try:
                table = self.tables[#tname.getText()]
            except KeyError:
                raise SemanticException(#tname, "undefined table")
		}
		( vname:NAME
			{ res = [(table[idx].getText(), {#vname.getText(): #(#[NUM, str(idx)])}) for idx in range(len(table))]}
		| tidx:NUM 
			{
                try:
                    res = [(table[int(#tidx.getText())], {})]
                except KeyError:
                    raise SemanticException(#tname, "index outside bounds")
            }
		))
	| d:DECOR
		{ res = [('.' + d.getText()[1:], {})] }
	;

// Expands variables, table references, and functions in RTL.
//
// NOTE: Especial care must be taken here in order to *duplicate* AST nodes, and 
// not simply refer to them, as that would result in corruption of the AST.
rtl_expand
	:! #( RTL 
			{ ## = #(#[RTL,"RTL"]) }
		(rt:rtl_expand
		 	{
                // do not nest RTL blocks
                if #rt.getType() == RTL:
                    if #rt.getFirstChild():
                        ##.addChild(#rt.getFirstChild())
                else:
                    ##.addChild(#rt)
		 	}
		)*)
	|! name:NAME 
        {
            s = #name.getText()
            if s in self.locals[-1]:
                ## = self.astFactory.dupTree(self.locals[-1][s])
            elif s in self.constants:
                ## = self.astFactory.dupTree(self.constants[s])
            else:
                ## = self.astFactory.dupTree(#name)
        }
    |! #(TABLE etname:NAME etindex:rtl_expand)
        {
            try:
                table = self.tables[#etname.getText()]
            except KeyError:
                ## = self.astFactory.dupTree(##_in)
                raise SemanticException(#etname, "undefined table")
            
            try:
                index = int(#etindex.getText())
            except ValueError:
                ## = self.astFactory.dupTree(##_in)
                raise SemanticException(#etname, "non-numeric indice")
           
            try:
                expr = table[index]
            except:
                raise SemanticException(#etname, "indice out of bounds")
           
            ## = self.astFactory.dupTree(expr)
        }
    |! #(LOOKUP_OP lexpr:rtl_expand otname:NAME otindex:rtl_expand rexpr:rtl_expand)
        {
            try:
                table = self.tables[#otname.getText()]
            except KeyError:
                ## = self.astFactory.dupTree(##_in)
                raise SemanticException(#otname, "undefined table")
            
            try:
                index = int(#otindex.getText())
            except ValueError:
                ## = self.astFactory.dupTree(##_in)
                raise SemanticException(#otname, "non-numeric indice")
           
            try:
                op = table[index]
            except:
                raise SemanticException(#otname, "indice out of bounds")
           
            op = self.astFactory.dupTree(op)
            ## = #(op, #lexpr, #rexpr)
        }
    |! #(FUNCTION fname:NAME { fargs = [] } (farg:rtl_expand { fargs.append(#farg) } )* )
        {
            try:
        	        fparams, fbody = self.functions[fname.getText()]
        	    except KeyError:
                ## = self.astFactory.dupTree(##_in)
                raise SemanticException(#fname, "undefined function")
            
            self.locals.append(dict(zip(fparams, fargs)))
            self.rtl_expand(fbody)
            ## = self.getAST()
            self.locals.pop()
        }
	| #( . ( rtl_expand )* )
		// recurse
	;

