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

header "translator.__init__" {
    self.globals = kwargs.get("globals", {})
    self.locals = kwargs.get("locals", {})
    self.stack = []
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
	LID;
	UID;
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
	REC = "rec";
	SWITCH = "switch";
	CASE = "case";
	OTHERWISE = "otherwise";
	VARMETHOD;
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

ID
options { testLiterals = true; }
	: 
		( 'a'..'z' ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
			{ $setType(LID) }
		| 'A'..'Z' ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
			{ $setType(UID) }
		| '_'
			{ $setType(WILDCARD) }
			( ('a'..'z'|'A'..'Z'|'0'..'9'|'_')+ 
				{ $setType(ID) } 
			)?
		)
		( ( '.' ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* )+
				{ $setType(ID) }
		| '-' ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
				{ $setType(VARMETHOD) }
		|
		)
	;

protected
PYSTR
options {generateAmbigWarnings = false;}
    : "'''" (options {greedy = false;}: ESC | EOL | . )* "'''"
    | "\"\"\"" (options {greedy = false;}: ESC | EOL | . )* "\"\"\""
	| '\'' ( ESC | ~'\'' )* '\''
	| '"' ( ESC | ~'"' )* '"'
	;

protected
ESC
    : '\\' ( EOL | . )
    ;

OBJ
	: 
		'`'! 
		( COMMENT
		| PYSTR
		| EOL
		| ~'`'
		)*
		'`'!
	;

LPAREN: '(';
RPAREN: ')';
LSQUARE: '[';
RSQUARE: ']';
LCURLY: '{';
RCURLY: '}';
LANGLE: '<';
RANGLE: '>';
RSLASH: '\\';
LSLASH: '/';

COMMA: ',';
QUEST: '?';
BANG: '!';
COLON: ':';
STAR: '*';
PLUS: '+';
MINUS: '-';
INTO: "->";
SEMI: ';';
CARET: '^';
VERT: '|';
TILDE: '~';
AT: '@';
EQUAL: '=';

APPLY_MATCH: "=>";


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
	JOIN;
}

transf_defs
	: ( transf_def )* EOF!
	;

rule_defs
	: ( rule_def )* EOF!
	;

transf_def
	: i:id EQUAL^ transf
	;

rule_def
	: id EQUAL^ rule_set
	;

transf
	: transf_expr
	;

transf_prefix
	: QUEST^ term
	| BANG^ term
	| TILDE^ term
	| EQUAL^ LID
	| LSLASH^ LID
	;

transf_method
	: v:VARMETHOD! ( LPAREN! arg_list RPAREN!)?
		{
            n, m = #v.getText().split('-')
            ## = #(#[VARMETHOD,"VARMETHOD"], #[ID,n], #[ID,m], ##) 
		}
	;

transf_atom
	: IDENT
	| FAIL
	| transf_prefix
	| transf_method
	| id ( LPAREN! arg_list RPAREN! )?
		{ ## = #(#[CALL,"CALL"], ##) }
	| LCURLY!
		( ( id_list COLON ) => id_list COLON transf
			{ ## = #(#[SCOPE,"SCOPE"], ##) } 
		| rule_set
		) RCURLY!
	| LPAREN!
		( ( term INTO ) =>  rule
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
	| REC^ id COLON! transf_atom
	;

transf_application
	: transf_atom ( APPLY_MATCH^ term )*
	;

transf_merge
	: transf_application 
		( RSLASH id_list LSLASH! ( LSLASH id_list RSLASH! )? transf_application 
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		| LSLASH id_list RSLASH! ( RSLASH id_list LSLASH! )? transf_application
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		)?
	;

transf_composition
	: transf_merge ( SEMI^ transf_merge )*
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

transf_list
	: ( transf ( COMMA! transf )* )?
	;

defn
	: id EQUAL! transf
	;

defn_list
	: defn ( COMMA! defn )*
	;

id
	: ID
	| l:LID { #l.setType(ID) }
	| u:UID { #u.setType(ID) }
	| w:WHERE { #w.setType(ID) }
	;

arg_list
	: ( arg ( COMMA! arg )* )?
	;

arg
	: OBJ
	| transf
	;
	
rule
	: term INTO! term ( WHERE transf )?
		{ ## = #(#[RULE,"RULE"], ##) }
	;

anon_rule
	: rule
		{ ## = #(#[ANON,"ANON"], ##) }
	;

rule_set
	: anon_rule 
		( VERT! rule_set
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

term
	: term_atom 
		( options { warnWhenFollowAmbig=false; }
		: term_anno
			{ ## = #(#[ANNOS,"ANNOS"], ##) }
		)?
	;

term_atom
	: INT
	| REAL
	| STR
	| LSQUARE! term_list RSQUARE!
	| term_sym
	| term_tuple
	| term_appl
	| term_var
	| WILDCARD
	| transf_prefix
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	| transf_method
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	| LANGLE! transf RANGLE!
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	;

term_name
	: u:UID
		{ ## = #(#[STR,#u.getText()]) }
	;

term_var
	: l:LID
		{ ## = #(#[VAR,#l.getText()]) }
	;

term_sym
	: term_name term_implicit_nil
		{ ## = #(#[APPL,"APPL"], ##) }
	;
	
term_tuple
	: term_args
		{ ## = #(#[APPL,"APPL"], #[STR,""], ##) }
	;
	
term_appl
	: ( term_name | term_var | WILDCARD ) term_args
		{ ## = #(#[APPL,"APPL"], ##) }
	;
	
term_args
	: LPAREN! term_list RPAREN!
	;

term_anno
	: LCURLY! term_list RCURLY!
	;

term_implicit_wildcard
	:
		{ ## = #(#[WILDCARD,"_"]) }
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
	: ( id ( COMMA! id )* )?
	;


class translator extends TreeParser;

options {
	defaultErrorHandler = false;
}

{
    // XXX: too much python voodoo
    
    def bind_transf_name(self, name):
        // lookup in the builtins module
        from transf.parse.builtins import builtins
        try:
            return builtins[name]
        except KeyError:
            pass
        
        // lookup in the symbol stack
        for i in range(len(self.stack) - 1, -1, -1):
            try:
                return self.stack[i][name]
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
    
    def define_transf_name(self, name, value):
        // define transf in the local namespace
        eval(compile(name + " = _", "", "single"), {"_": value}, self.locals)
}

transf_defs
	: ( transf_def )+
	;
	
transf_def
	: #( EQUAL n=id t=transf )
		{ self.define_transf_name(n, t) }
	;

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
	| #( EQUAL n=id )
		{ ret = transf.variable.Set(n) }
	| #( LSLASH n=id )
		{ ret = transf.variable.Unset(n) }
	| #( SEMI l=transf r=transf )
		{ ret = transf.combine.Composition(l, r) }
	| #( PLUS l=transf r=transf )
		{ ret = transf.combine.Choice(l, r) }
	| #( LANGLE l=transf m=transf r=transf )
		{ ret = transf.combine.GuardedChoice(l, m, r) }
	| #( CALL n=id
		{ args = [] } 
		( a=arg { args.append(a) } )*
		// TODO: handle term args
		{
            txn = self.bind_transf_name(n)
            if txn is None:
                ret = None
                raise SemanticException(#i, "could not find %s" % n)
            if isinstance(txn, transf.base.Transformation):
                // TODO: check args
                ret = txn
            else:
                ret = txn(*args) 
        }
	  )
	| #( SCOPE vars=id_list COLON ret=transf )
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
		( n=id v=transf
			{ vars[n] = v }
		)* IN t=transf
	  )
	  	{ ret = transf.scope.Let(t, **vars) }
	| #( JOIN l=transf 
			{ unames = [] }
			{ inames = [] }
		( LSLASH ids=id_list 
			{ inames.extend(ids) }
		| RSLASH ids=id_list
			{ unames.extend(ids) }
		)* r=transf
	 ) 
		{ ret = transf.table.Join(l, r, unames, inames) }
	| #( REC 
			{ ret = transf.base.Proxy() }
		r=id 
			{ self.stack.append({r: ret}) }
		t=transf
			{ self.stack.pop() }
			{ ret.subject = t }
	  )
	| #( VARMETHOD v=id m=id a=arg_list )
		{ ret = transf.variable.Wrap(v, m, *a) }
	;

arg_list returns [ret]
	: { ret = [] } ( a=arg  { ret.append(a) } )*
	;
	
arg returns [ret]
	: o:OBJ
		{ ret = eval(#o.getText(), self.globals, self.locals) }
	| ret=transf
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
	| v:VAR
		{ ret = transf.traverse.Var(#v.getText()) }
	| #( ANNOS t=traverse_term a=traverse_term )
		{ ret = t & transf.traverse.Annos(a) }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

id_list returns [ret]
	: { ret = [] } ( i=id  { ret.append(i) } )*
	;

id returns [ret]
	: i:ID
		{ ret = #i.getText() }
	| l:LID
		{ ret = #l.getText() }
	| u:LID
		{ ret = #u.getText() }
	;