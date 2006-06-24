/* 
 * Grammar for generating term transformations. The syntax is inspired on 
 * the Stratego language.
 */


header {
    import antlr
    import aterm.factory
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


class parser extends Parser;

options {
	k=2;
	buildAST = true;
	defaultErrorHandler = false;
}

tokens {
	TRANSF_DEF;
	TRANSF_FAC_DEF;
	TRANSF;
	TRANSF_FAC;
	SCOPE;
	RULE;
	ANON;
	BUILD_APPLY;
	JOIN;
	ITERATE;
	TERM;
	TABLE;
	NIL;
	CONS;
	UNDEF;
	APPL;
	ANNOS;
	VAR;
}

transf_defs
	: ( transf_def )* EOF!
	;

rule_defs
	: ( rule_def )* EOF!
	;

meta_def
	: id_list COLON transf EOF!
	;

transf_def
	: id EQUAL! transf
		{ ## = #(#[TRANSF_DEF,"TRANSF_DEF"], ##) }
	| id LPAREN! id_list RPAREN! EQUAL transf	
		{ ## = #(#[TRANSF_FAC_DEF,"TRANSF_FAC_DEF"], ##) }
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
	| EQUAL^ (PLUS | MINUS)? LID (LPAREN! arg_list RPAREN!)?
	| CARET^ LID
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
	| id 
		( 
			{ ## = #(#[TRANSF,"TRANSF"], ##) }
		| LPAREN! arg_list RPAREN!
			{ ## = #(#[TRANSF_FAC,"TRANSF_FAC"], ##) }
		)
	| LCURLY!
		( ( id_list COLON ) => id_list COLON transf
			{ ## = #(#[SCOPE,"SCOPE"], ##) } 
		| rule_set
		) RCURLY!
	| LPAREN!
		( ( term RARROW ) =>  rule
		| transf
		) RPAREN!
	| LANGLE! transf RANGLE! term
		{ ## = #(#[BUILD_APPLY,"BUILD_APPLY"], ##) }
	| IF^ transf THEN! transf 
		( ELIF! transf THEN! transf )*
		( ELSE transf )? 
	  END!
	| SWITCH^ transf 
		( CASE term ( COMMA! term )* COLON! transf )* 
		( OTHERWISE COLON! transf )? 
	  END!
	| LET^ defn_list IN transf END!
	| REC^ id COLON! transf_atom
	| WITH^ var_def_list IN transf END!
	;

transf_application
	: transf_atom ( RDARROW^ var )?
	;

transf_merge
	: transf_application 
		( RSLASH id_list LSLASH! ( LSLASH id_list RSLASH! )? transf_application 
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		| LSLASH id_list RSLASH! ( RSLASH id_list LSLASH! )? transf_application
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		)?
	| RSLASH id_list LSLASH! ( LSLASH id_list RSLASH! )? STAR! transf_application 
		{ ## = #(#[ITERATE,"ITERATE"], ##) } 
	| LSLASH id_list RSLASH! ( RSLASH id_list LSLASH! )? STAR! transf_application
		{ ## = #(#[ITERATE,"ITERATE"], ##) } 
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

transf_undeterministic_choice
	: transf_choice ( VERT^ transf_choice ( VERT! transf_choice )* )?
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

var_def_list
	: var_def (COMMA! var_def )*
	;

var_def
	: var constructor
	;

constructor
	: ( EQUAL! transf )?
		{ ## = #(#[TERM,"TERM"], ##) }
	| LSQUARE! RSQUARE! ( EQUAL! var )?
		{ ## = #(#[TABLE,"TABLE"], ##) }
	| LPAREN! RPAREN! ( EQUAL! transf )?
		{ ## = #(#[DYNAMIC,"DYNAMIC"], ##) }
	;

var
	: l:LID	{ #l.setType(VAR) }
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
	| PRIME! var ( PRIME! )?
	| transf
	;
	
rule
	: term RARROW! term ( WHERE transf )?
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
//	| transf_prefix
	//	{ ## = #(#[TRANSF,"TRANSF"], ##) }
	| transf_method
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
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
	| LANGLE! transf RANGLE!
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	;

term_name
	: u:UID
		{ ## = #(#[STR,#u.getText()]) }
	;

term_var
	: var
	;

term_sym
	: term_name term_undefined
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

term_undefined
	:
		{ ## = #(#[UNDEF,"UNDEF"]) }
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
