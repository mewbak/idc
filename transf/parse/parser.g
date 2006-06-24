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
	importVocab = antlraterm;
}

transf_defs
	: ( transf_def )* EOF!
		{ ## = #([ATAPPL,"Defs"],#([ATLIST], ##)) }
	;

rule_defs
	: ( rule_def )* EOF!
		{ ## = #([ATAPPL,"Defs"],#([ATLIST], ##)) }
	;

meta_def
	: id_list COLON! transf EOF!
		{ ## = #([ATAPPL,"MetaDef"], ##) }
	;

transf_def
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"TransfDef"], ##) }
	| id LPAREN! id_list RPAREN! EQUAL! transf	
		{ ## = #(#[ATAPPL,"TransfFacDef"], ##) }
	;
	


rule_def
	: id EQUAL^ rule_set
		{ ## = #(#[ATAPPL,"RuleDef"], ##) }
	;

transf
	: transf_expr
	;

transf_prefix
	: QUEST! term
		{ ## = #(#[ATAPPL,"Match"], ##) }
	| BANG! term
		{ ## = #(#[ATAPPL,"Build"], ##) }
	| TILDE! term
		{ ## = #(#[ATAPPL,"Traverse"], ##) }
	| EQUAL! var
		{ ## = #(#[ATAPPL,"Set"], ##) }
	;

transf_atom
	: IDENT!
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	| FAIL!
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	| transf_prefix
	| id 
		( 
			{ ## = #(#[ATAPPL,"Transf"], ##) }
		| LPAREN! arg_list RPAREN!
			{ ## = #(#[ATAPPL,"TransfFac"], ##) }
		)
	| LCURLY!
		( ( id_list COLON! ) => id_list COLON! transf
			{ ## = #(#[ATAPPL,"Scope"], ##) } 
		| rule_set
		) RCURLY!
	| LPAREN!
		( ( term RARROW ) =>  rule
		| transf
		) RPAREN!
	| LANGLE! transf RANGLE! term
		{ ## = #(#[ATAPPL,"BuildApply"], ##) }
	| ( IF ) => if_clauses if_else END!
		{ ## = #(#[ATAPPL,"If"], ##) }
	| SWITCH! transf switch_cases switch_otherwise END!
		{ ## = #(#[ATAPPL,"Switch"], ##) }
	| LET! defn_list IN! transf END!
		{ ## = #(#[ATAPPL,"Let"], ##) }
	| REC! id COLON! transf_atom
		{ ## = #(#[ATAPPL,"Rec"], ##) }
	| WITH! var_def_list IN! transf END!
		{ ## = #(#[ATAPPL,"With"], ##) }
	;

if_clauses
	: ( if_clause )*
		{ ## = #(#[ATLIST], ##) }
	;
	
if_clause
	: IF! transf THEN! transf 
		{ ## = #(#[ATAPPL,"IfClause"], ##) }
	| ELIF! transf THEN! transf
		{ ## = #(#[ATAPPL,"IfClause"], ##) }
	;
	
if_else
	: ELSE! transf
	| { ## = #(#[ATAPPL,"Ident"], ##) }
	;
	
switch_cases
	: ( switch_case )*
		{ ## = #(#[ATLIST], ##) }
	;
	
switch_case
	: CASE! switch_case_terms COLON! transf
		{ ## = #(#[ATAPPL,"SwitchCase"], ##) }
	;
	
switch_case_terms
	: term ( COMMA! term )*
		{ ## = #(#[ATLIST], ##) }
	;

switch_otherwise
	: OTHERWISE! COLON! transf
	|
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	;
	
transf_application
	: transf_atom 
		( RDARROW! var 
			{ ## = #(#[ATAPPL,"Store"], ##) } 
		)?
	;

transf_merge
	:! l:transf_application 
		( n:transf_merge_names r:transf_application
		{ ## = #(#[ATAPPL,"Join"], #l, #r, #n) } 
		|
		{ ## = #l } 
		)
	|! n2:transf_merge_names STAR! o:transf_application
		{ ## = #(#[ATAPPL,"Iterate"], #o, #n2) } 
	;

transf_merge_names
	: transf_merge_union_names transf_merge_opt_isect_names
	|! i:transf_merge_isect_names u:transf_merge_opt_union_names
		{ ## = #i }
		{ ##.setNextSibling(#u) }
	;

transf_merge_union_names
	: LSLASH! id_list RSLASH!
	;

transf_merge_isect_names
	: RSLASH! id_list LSLASH!
	;

transf_merge_opt_union_names
	: transf_merge_union_names
	| 
		{ ## = #([ATLIST]) }
	;

transf_merge_opt_isect_names
	: transf_merge_isect_names
	| 
		{ ## = #([ATLIST]) }
	;

transf_composition
	: transf_merge 
		( SEMI! transf_composition 
			{ ## = #(#[ATAPPL,"Composition"], ##) }	
		)?
	;

transf_choice
	: transf_composition 
		( LANGLE! transf_composition PLUS! transf_choice
			{ ## = #(#[ATAPPL,"GuardedChoice"], ##) }	
		| PLUS! transf_choice 
			{ ## = #(#[ATAPPL,"LeftChoice"], ##) }	
		)?
	;

transf_undeterministic_choice
	: transf_choice 
		( VERT! transf_undeterministic_choice 
			{ ## = #(#[ATAPPL,"Choice"], ##) }	
		)?
	;

transf_expr
	: transf_choice
	;

transf_list
	: ( transf ( COMMA! transf )* )?
		{ ## = #(#[ATLIST], ##) }
	;

defn_list
	: defn ( COMMA! defn )*
		{ ## = #(#[ATLIST], ##) }
	;

defn
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"LetDef"], ##) }
	;

var_def_list
	: var_def (COMMA! var_def )*
		{ ## = #(#[ATLIST], ##) }
	;

var_def
	: var constructor
		{ ## = #(#[ATAPPL,"VarDef"], ##) }
	;

constructor
	: 
		{ ## = #(#[ATAPPL,"Term"], ##) }
	| EQUAL! transf
		{ ## = #(#[ATAPPL,"TermTransf"], ##) }
	| LSQUARE! RSQUARE! 
		( EQUAL! var 
		{ ## = #(#[ATAPPL,"TableCopy"], ##) }
		|
		{ ## = #(#[ATAPPL,"Table"], ##) }
		)
	| LPAREN! RPAREN! ( EQUAL! transf )?
		{ ## = #(#[ATAPPL,"Dynamic"], ##) }
	;

var
	: LID
		{ ## = #(#[ATAPPL,"Var"], #([ATSTR],##)) }
	;

id
	: ( ID | LID | UID | WHERE ) 
		{ ## = #(#[ATAPPL,"Id"], #([ATSTR],##)) }
	;

arg_list
	: ( arg ( COMMA! arg )* )?
		{ ## = #(#[ATLIST], ##) }
	;

arg
	: OBJ
			{ ## = #(#[ATAPPL,"Obj"], #([ATSTR],##)) }
	| PRIME! var ( PRIME! )?
	| transf
	;
	
rule
	: term RARROW! term 
		( WHERE transf 
			{ ## = #(#[ATAPPL,"WhereRule"], ##) }
		|
			{ ## = #(#[ATAPPL,"Rule"], ##) }
		)
	;

anon_rule
	: rule
		{ ## = #(#[ATAPPL,"Anon"], ##) }
	;

rule_set
	: anon_rule 
		( VERT! rule_set
			{ ## = #(#[ATAPPL,"Choice"], ##) }
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
			{ ## = #(#[ATAPPL,"Annos"], ##) }
		)?
	| transf_prefix
	;

term_atom
	: INT
		{ ## = #(#[ATAPPL,"Int"], #([ATINT],##)) }
	| REAL
		{ ## = #(#[ATAPPL,"Real"], #([ATREAL],##)) }
	| STR
		{ ## = #(#[ATAPPL,"Str"], #([ATSTR],##)) }
	| LSQUARE! term_list RSQUARE!
	| term_sym
	| term_tuple
	| term_appl
	| term_var
	| term_wildcard
	| LANGLE! transf RANGLE!
		{ ## = #(#[ATAPPL,"Transf"], ##) }
	;

term_name
	: UID
		{ ## = #([ATAPPL,"Str"],#([ATSTR],##)) }
	;

term_var
	: var
	;

term_sym
	: term_name term_undefined
		{ ## = #(#[ATAPPL,"Appl"], ##) }
	;
	
term_tuple
	: term_args
		{ ## = #(#[ATAPPL,"Appl"], #[ATSTR,""], ##) }
	;
	
term_appl
	: ( term_name | term_var | term_wildcard ) term_args
		{ ## = #(#[ATAPPL,"Appl"], ##) }
	;
	
term_args
	: LPAREN! term_list RPAREN!
	;

term_undefined
	:
		{ ## = #(#[ATAPPL,"Undef"]) }
	;
	
term_wildcard
	: WILDCARD!
		{ ## = #(#[ATAPPL,"Wildcard"]) }	
	;
	
term_anno
	: LCURLY! term_list RCURLY!
	;

term_implicit_wildcard
	:
		{ ## = #(#[ATAPPL,"Wildcard"]) }	
	;

term_opt_args
	: ( LPAREN ) => term_args
	| term_implicit_nil
	;
	
term_implicit_nil
	:
		{ ## = #(#[ATAPPL,"Nil"]) }	
	;

term_list
	: term_implicit_nil
	| term ( COMMA! term_list | term_implicit_nil )
		{ ## = #(#[ATAPPL,"Cons"], ##) }	
	| STAR! term_opt_wildcard
	;
	
term_opt_wildcard
	: term
	| term_implicit_wildcard
	;

id_list
	: ( id ( COMMA! id )* )?
		{ ## = #([ATLIST],##) }
	;

