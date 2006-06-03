/* 
 * Grammar for generating term transformations. The syntax is inspired on 
 * the Stratego language.
 */


header {
    import transf
}

header "compiler.__init__" {
    self.globals = kwargs.get("globals", {})
    self.locals = kwargs.get("locals", {})
}


options {
	language = "Python";
}


class lexer extends Lexer;

options {
	k = 2;
	testLiterals = false;
}

tokens {
	INT;
	REAL;
	VAR;
	WILDCARD = "_";
	WHERE = "where";
	IF = "if";
	THEN = "then";
	ELSE = "else";
	END = "end";
	IDENT = "id";
	FAIL = "fail";
}

protected
EOL
	:
		( '\r'
			( ( '\n' ) => '\n' 
			|
			)
		| '\n'
		)
		{ $newline }
	;
	
// Whitespace -- ignored
WS	
	: ( ' ' | '\t' | '\f' | EOL )+ 
		{ $setType(SKIP); }
	;

// TODO: handle comments terminated by EOF
COMMENT
    : 
		"#" 
		( ~('\n'|'\r') )*
		( EOL )
			{ $setType(SKIP); }
	;

REAL_OR_INT
	:
		{ $setType(INT); }
		// sign
		('-')?
		// fraction
		( ('0'..'9')+ ( '.' ('0'..'9')* { $setType(REAL); } )?
		| '.' ('0'..'9')+ { $setType(REAL); }
		)
		// exponent
		( ('e'|'E') ('-'|'+')? ('0'..'9')+ { $setType(REAL); } )?
	;

STR
	: '"'! ( CHAR )* '"'!
	;

protected
CHAR
	:
		'\\'!
		( 'n' { $setText("\n"); }
		| 'r' { $setText("\r"); }
		| 't' { $setText("\t"); }
		| '"' { $setText("\""); }
		| ~('n'|'r'|'t'|'"')
		)
	| ~('"'|'\\')
	;

protected
ID_ATOM
	: ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
	;

ID
options { testLiterals = true; }
	: ID_ATOM ( '.' ID_ATOM )*
	;
	
LPAREN: '(';
RPAREN: ')';

LSQUARE: '[';
RSQUARE: ']';

LCURLY: '{';
RCURLY: '}';

LANGLE: '<';
RANGLE: '>';

COMMA: ',';

QUEST: '?';

COLON: ':';

STAR: '*';

PLUS: '+';

INTO: "->";

SEMI: ';';

CARET: '^';

BANG: '!';

VERT: '|';

RSLASH: '\\';

NOT_OP: '~';

AT: '@';


class parser extends Parser;

options {
	k=3;
	buildAST = true;
}

tokens {
	APPL;
	NIL;
	CONS;
	CALL;
	RULE;
	SCOPE;
	LAMBDA_RULE;
	TRANSF;
}

grammar
	: transf EOF!
	;

transf_atom
	: IDENT
	| FAIL
	| QUEST^ term
	| BANG^ term
	| ID LPAREN! transf_list ( VERT term_arg_list )? RPAREN!
		{ ## = #(#[CALL,"CALL"], ##) }
	| LCURLY! id_list COLON transf RCURLY!
		{ ## = #(#[SCOPE,"SCOPE"], ##) }
	| LPAREN! transf RPAREN!
/* TODO: handle non-anonymous rules
	| LPAREN! rule RPAREN!
		{ ## = #(#[RULE,"RULE"], ##) }
*/
	| RSLASH! rule RSLASH!
		{ ## = #(#[LAMBDA_RULE,"LAMBDA_RULE"], ##) }
	| 
	;

transf_composition
	: transf_atom ( SEMI^ transf_atom )*
	;

transf_choice
	: transf_composition ( PLUS^ transf_composition )*
	;

transf_expr
	: transf_choice
	;

transf
	: transf_expr
	;

transf_list
	: ( transf ( COMMA! transf )* )?
	;

term_arg_list
	: ( term ( COMMA! term )* )?
	;

rule
	: term INTO term ( WHERE transf )?
		{ ## = #(#[RULE,"RULE"], ##) }
	;

rule_def
	: rule ( VERT^ rule )*
	;

/*
debug_term
	: t:term
		{
            if self.debug:
                import sys
                sys.stderr.write("*** Term ***\n")
                sys.stderr.write(#t.toStringTree())
                sys.stderr.write("\n")
		}
	;
*/

term
	: INT
	| REAL
	| STR
	| LSQUARE! term_list RSQUARE!
	| term_args
		{ ## = #(#[APPL,"APPL"], #[CONS,""], ##) }
	| i:ID 
		{
            inicial = #i.getText()[0]
        }
        ( { inicial.isupper() }?
        	{ #i.setType(STR) } 
        	term_opt_args 
			{ ## = #(#[APPL,"APPL"], ##) }
        | 
        	{ #i.setType(VAR) } 
        	( term_args 
				{ ## = #(#[APPL,"APPL"], ##) }
        	//| AT! term
        	| 
        	)
        )
	| WILDCARD ( term_args { ## = #(#[APPL,"APPL"], ##) } )?
	| LANGLE! transf RANGLE!
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	;

term_implicit_wildcard
	:
		{ ## = #(#[WILDCARD,"_"]) }
	;

term_args
	: LPAREN! term_list RPAREN!
	;

term_opt_args
	: ( LPAREN ) => term_args
	| term_implicit_nil
	;
	
term_implicit_nil
	:
		{ ## = #(#[NIL,"NIL"]) }	
	;

term_list
	: term_implicit_nil
	| term ( COMMA! term_list | term_implicit_nil )
		{ ## = #(#[CONS,"CONS"], ##) }	
	| STAR! term_opt_wildcard
	;
	
term_opt_wildcard
	: term
	|
		{ ## = #(#[WILDCARD,"_"]) }	
	;

id_list
	: ( ID ( COMMA! ID )* )?
	;


{
    builtin_table = {
        "all": transf.traversal.All,
        //"one": transf.traversal.One,
        //"some": transf.traversal.Some,
        "not": transf.combinators.Not,
        "where": transf.combinators.Where,
    }
}

class compiler extends TreeParser;

{
    def bind_transf_name(self, name):
        // TODO: handle caller global and local namespaces
    
        // lookup in the caller namespace
        try:
            return eval(name, self.globals, self.locals)
        except NameError:
            pass
    
        // lookup in the transf module
        try:
            return getattr(transf, name)
        except AttributeError:
            pass
        
        // lookup in the builtin table
        try:
            return builtin_table[name]
        except KeyError:
            pass
        
        return None
}

transf returns [ret]
	: IDENT
		{ ret = transf.combinators.Ident() }
	| FAIL
		{ ret = transf.combinators.Fail() }
	| #( QUEST m=match_term )
		{ ret = m }
	| #( BANG b=build_term )
		{ ret = b }
	| #( SEMI l=transf r=transf )
		{ ret = transf.combinators.Composition(l, r) }
	| #( PLUS l=transf r=transf )
		{ ret = transf.combinators.Choice(l, r) }
	| #( CALL i:ID
		{ args = [] } 
		( a=transf { args.append(a) } )*
		// TODO: handle term args
		{
            name = #i.getText()
            // TODO: better error handling
            txn = self.bind_transf_name(name)
            ret = txn(*args) 
        }
	  )
	| #( SCOPE
		{ vars = [] } 
		( v:ID { vars.append(#v.getText()) } )*
		COLON
		t=transf 
	  )
		{ ret = transf.scope.Scope(t, vars) }
	;

rule returns [ret]
	: #( RULE m=match_term b=build_term )
		{ ret = transf.combinators.Composition(m, b) }
	| #( LAMBDA_RULE m=p:match_term b=build_term )
		{
            vars = []
            self.collect_term_vars(#p, vars)
            ret = transf.combinators.Composition(m, b)
            ret = transf.scope.Scope(ret, vars)
        }
	| #( VERT l=rule r=rule )
		{ ret = transf.combinators.Choice(l, r) }
	;



match_term returns [ret]
	: i:INT 
		{ ret = transf.matching.MatchInt(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.matching.MatchReal(float(#r.getText())) }
	| s:STR 
		{ ret = transf.matching.MatchStr(#s.getText()) }
	| NIL
		{ ret = transf.matching.MatchNil() }
	| #( CONS h=match_term t=match_term )
		{ ret = transf.matching.MatchCons(h, t) }
	| #( APPL n=match_term a=match_term )
		{ ret = transf.matching.MatchAppl(n, a) }
	| w:WILDCARD 
		{ ret = transf.combinators.Ident() }
	| #( v:VAR 
		{ ret = transf.matching.MatchVar(#v.getText()) }
		( p=match_term
			{ ret = transf.combinators.composition(p, ret) }
		)?
	  )
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

collect_term_vars[vars]
	: INT 
	| REAL 
	| STR 
	| NIL
	| #( CONS collect_term_vars[vars] collect_term_vars[vars] )
	| #( APPL collect_term_vars[vars] collect_term_vars[vars] )
	| WILDCARD 
	| #( v:VAR ( collect_term_vars[vars] )? )
		{
            name = #v.getText()
            if name not in vars:
                vars.append(name)
        }
	| TRANSF
	;

build_term returns [ret]
	: i:INT 
		{ ret = transf.building.BuildInt(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.building.BuildReal(float(#r.getText())) }
	| s:STR 
		{ ret = transf.building.BuildStr(#s.getText()) }
	| NIL
		{ ret = transf.building.BuildNil() }
	| #( CONS h=build_term t=build_term )
		{ ret = transf.building.BuildCons(h, t) }
	| #( APPL n=build_term a=build_term )
		{ ret = transf.building.BuildAppl(n, a) }
	| w:WILDCARD 
		{ ret = transf.combinators.Ident() }
	| v:VAR 
		{ ret = transf.building.BuildVar(#v.getText()) }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

