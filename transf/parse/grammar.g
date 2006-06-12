/* 
 * Grammar for generating term transformations. The syntax is inspired on 
 * the Stratego language.
 */


header {
    import antlr
    import transf


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
	IDENT = "id";
	FAIL = "fail";
	IF = "if";
	THEN = "then";
	ELSE = "else";
	END = "end";
	LET = "let";
	IN = "in";
	WHERE = "where";
	SWITCH = "switch";
	CASE = "case";
	OTHERWISE = "otherwise";
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

APPLY_MATCH: "=>";

SEMI: ';';

CARET: '^';

BANG: '!';

VERT: '|';

RSLASH: '\\';

TILDE: '~';

AT: '@';

EQUAL: '=';


class parser extends Parser;

options {
	k=3;
	buildAST = true;
	defaultErrorHandler = false;
}

tokens {
	APPL;
	NIL;
	CONS;
	ANNOS;
	CALL;
	RULE;
	SCOPE;
	ANON;
	TRANSF;
	BUILD_APPLY;
}

tgrammar
	: transf EOF!
	;

rgrammar
	: rule_def EOF!
	;

transf_atom
	: IDENT
	| FAIL
	| QUEST^ term
	| BANG^ term
	| TILDE^ term
	| id ( LPAREN! transf_list ( VERT term_arg_list )? RPAREN! )?
			{ ## = #(#[CALL,"CALL"], ##) }
	| LCURLY!
		( ( id_list COLON ) => id_list COLON transf
			{ ## = #(#[SCOPE,"SCOPE"], ##) } 
		| anon_rule
		) RCURLY!
	| LPAREN!
		( ( term INTO ) => rule_def 
		| transf
		) RPAREN!
	| LANGLE! transf RANGLE! term
		{ ## = #(#[BUILD_APPLY,"BUILD_APPLY"], ##) }
	| IF^ transf THEN! transf ( ELSE! transf )? END!
	| LET^ defn_list IN transf END!
	| SWITCH^ transf 
		( CASE transf COLON! transf )* 
		( OTHERWISE COLON! transf )? 
	  END!
	;

defn
	: ID EQUAL! transf
	;

defn_list
	: defn ( COMMA! defn )*
	;

id
	: ID
	| w:WHERE { #w.setType(ID) }
	;

transf_application
	: transf_atom ( APPLY_MATCH^ term )*
	;

transf_composition
	: transf_application ( SEMI^ transf_application )*
	;

transf_choice
	: transf_composition 
		( LANGLE^ transf_composition PLUS! transf_choice
		| PLUS^ transf_choice 
		)?
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
	: term INTO! term ( WHERE transf )?
		{ ## = #(#[RULE,"RULE"], ##) }
	;

anon_rule
	: rule
		{ ## = #(#[ANON,"ANON"], ##) }
	;

rule_def
	: anon_rule 
		( VERT! rule_def 
			{ ## = #(#[PLUS,"PLUS"], ##) }
		)?
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

term_atom
	: INT
	| REAL
	| STR
	| LSQUARE! term_list RSQUARE!
	| term_args
		{ ## = #(#[APPL,"APPL"], #[CONS,""], ##) }
	| i:ID 
        ( { #i.getText()[0].isupper() }?
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

term
	: term_atom 
		( LCURLY! term_list RCURLY!
			{ ## = #(#[ANNOS,"ANNOS"], ##) }
		)?
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


class compiler extends TreeParser;

options {
	defaultErrorHandler = false;
}

{
    def bind_transf_name(self, name):
        // TODO: handle caller global and local namespaces
    
        // lookup in the builtins module
        from transf.parse.builtins import builtins
        try:
            return builtins[name]
        except KeyError:
            pass
        
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
        
        return None
}

transf returns [ret]
	: IDENT
		{ ret = transf.base.ident }
	| FAIL
		{ ret = transf.base.fail }
	| #( QUEST m=match_term )
		{ ret = m }
	| #( BANG b=build_term )
		{ ret = b }
	| #( TILDE t=traverse_term )
		{ ret = t }
	| #( SEMI l=transf r=transf )
		{ ret = transf.combine.Composition(l, r) }
	| #( PLUS l=transf r=transf )
		{ ret = transf.combine.Choice(l, r) }
	| #( LANGLE l=transf m=transf r=transf )
		{ ret = transf.combine.GuardedChoice(l, m, r) }
	| #( CALL i:ID
		{ args = [] } 
		( a=transf { args.append(a) } )*
		// TODO: handle term args
		{
            name = #i.getText()
            txn = self.bind_transf_name(name)
            if txn is None:
                ret = None
                raise SemanticException(#i, "could not find %s" % name)
            if isinstance(txn, transf.base.Transformation):
                // TODO: check args
                ret = txn
            else:
                ret = txn(*args) 
        }
	  )
	| #( SCOPE
		{ vars = [] } 
		( v:ID { vars.append(#v.getText()) } )*
		COLON
		ret=transf 
	  )
		{
            if vars:
                ret = transf.scope.Local(ret, vars)
        }
	| #( RULE m=match_term b=build_term
		( WHERE w=transf 
			{ ret = transf.combine.Composition(transf.combine.Where(w), b) }
		|
			{ ret = b }
		)
			{ ret = transf.combine.Composition(m, ret) }
	  )
	| #( ANON ret=at:transf )
		{
            vars = []
            self.collect_transf_vars(#at, vars)
            if vars:
                ret = transf.scope.Local(ret, vars)
        }
	| #( APPLY_MATCH t=transf m=match_term )
		{ ret = transf.combine.Composition(t, m) }
	| #( BUILD_APPLY t=transf b=build_term )
		{ ret = transf.combine.Composition(b, t) }
	| #( IF c=transf t=transf 
		(
			{ ret = transf.combine.IfThen(c, t) }
		| e=transf
			{ ret = transf.combine.IfThenElse(c, t, e) }
		)
	  )
	| #( SWITCH cond=transf 
			{ cases = [] }
		( CASE c=transf a=transf
			{ cases.append((c, a)) }
		)*
		( OTHERWISE o=transf
		|
			{ o=None }
		)
			{ ret = transf.sugar.Switch(cond, cases, o) }
	  )
	| #( LET 
			{ vars = {} }
		( n:ID v=transf
			{ vars[#n.getText()] = v }
		)* IN t=transf
	  )
	  	{ ret = transf.scope.Let(t, **vars) }
	;
	
match_term returns [ret]
	: i:INT 
		{ ret = transf.match.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.match.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.match.Str(#s.getText()) }
	| NIL
		{ ret = transf.match.nil }
	| #( CONS h=match_term t=match_term )
		{ ret = transf.match.Cons(h, t) }
	| #( APPL n=match_term a=match_term )
		{ ret = transf.match.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| #( v:VAR // TODO: handle sub-patterns
		{ ret = transf.match.Var(#v.getText()) }
		( p=match_term
			{ ret = transf.combine.composition(p, ret) }
		)?
	  )
	| #( ANNOS t=match_term a=match_term )
		{ ret = t & transf.match.Annos(a) }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

collect_transf_vars[vars]
	: #( RULE collect_term_vars[vars] )
	| .
	;

collect_term_vars[vars]
	: INT | REAL | STR 
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
	| #( ANNOS collect_term_vars[vars] collect_term_vars[vars] )
	| TRANSF
	;

build_term returns [ret]
	: i:INT 
		{ ret = transf.build.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.build.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.build.Str(#s.getText()) }
	| NIL
		{ ret = transf.build.nil }
	| #( CONS h=build_term t=build_term )
		{ ret = transf.build.Cons(h, t) }
	| #( APPL n=build_term a=build_term )
		{ ret = transf.build.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| v:VAR 
		{ ret = transf.build.Var(#v.getText()) }
	| #( ANNOS t=build_term a=build_term )
		{ ret = t & transf.build.Annos(a) }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

traverse_term returns [ret]
	: i:INT 
		{ ret = transf.match.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.match.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.match.Str(#s.getText()) }
	| NIL
		{ ret = transf.match.nil }
	| #( CONS h=traverse_term t=traverse_term )
		{ ret = transf.traverse.Cons(h, t) }
	| #( APPL n=traverse_term a=traverse_term )
		{ ret = transf.traverse.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| #( v:VAR // TODO: handle sub-patterns
		{ ret = transf.match.Var(#v.getText()) }
		( p=match_term
			{ ret = transf.combine.composition(p, ret) }
		)?
	  )
	| #( ANNOS t=traverse_term a=traverse_term )
		{ ret = t & transf.traverse.Annos(a) }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

