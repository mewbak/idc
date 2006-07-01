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
		{ ## = #(#[ATAPPL,"Defs"],#(#[ATLIST], ##)) }
	;

rule_defs
	: ( rule_def )* EOF!
		{ ## = #(#[ATAPPL,"Defs"],#(#[ATLIST], ##)) }
	;

meta_def
	: id_list COLON! transf EOF!
		{ ## = #(#[ATAPPL,"MetaDef"], ##) }
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

transf_atom
	: QUEST! term
		{ ## = #(#[ATAPPL,"Match"], ##) }
	| BANG! term
		{ ## = #(#[ATAPPL,"Build"], ##) }
	| TILDE! term
		{ ## = #(#[ATAPPL,"Traverse"], ##) }
	| EQUAL! id
		{ ## = #(#[ATAPPL,"Set"], ##) }
	| CARET! id
		{ ## = #(#[ATAPPL,"Unset"], ##) }
	;

transf_construct
	: IDENT!
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	| FAIL!
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	| transf_atom
	| id 
		( 
			{ ## = #(#[ATAPPL,"Transf"], ##) }
		| LPAREN! args RPAREN!
			{ ## = #(#[ATAPPL,"TransfFac"], ##) }
		)
	| LCURLY!
		( ( id_list COLON! ) => id_list COLON! transf
			{ ## = #(#[ATAPPL,"Scope"], ##) } 
		| rule_set
		) RCURLY!
	| LPAREN!
		( ( term RARROW ) => rule_set
		| transf
		) RPAREN!
	| LANGLE! transf RANGLE! term
		{ ## = #(#[ATAPPL,"BuildApply"], ##) }
	| IF! if_clauses if_else END!
		{ ## = #(#[ATAPPL,"If"], ##) }
	| SWITCH! transf switch_cases switch_else END!
		{ ## = #(#[ATAPPL,"Switch"], ##) }
	| LET! let_defs IN! transf END!
		{ ## = #(#[ATAPPL,"Let"], ##) }
	| WITH! with_defs IN! transf END!
		{ ## = #(#[ATAPPL,"With"], ##) }
	| REC! id COLON! transf_construct
		{ ## = #(#[ATAPPL,"Rec"], ##) }
	;

args
	: ( arg ( COMMA! arg )* )?
		{ ## = #(#[ATLIST], ##) }
	;

arg
	: OBJ
		{ ## = #(#[ATAPPL,"Obj"], #(#[ATSTR],##)) }
	| PRIME! id ( PRIME! )?
		{ ## = #(#[ATAPPL,"Var"], ##) }
	| transf
	;

if_clauses
	: if_clause (ELIF! if_clause)*
		{ ## = #(#[ATLIST], ##) }
	;
	
if_clause
	: transf THEN! transf 
		{ ## = #(#[ATAPPL,"IfClause"], ##) }
	;
	
if_else
	: ELSE! transf
	|
		{ ## = #(#[ATAPPL,"Ident"], ##) }
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

switch_else
	: ELSE! COLON! transf
	|
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	;

let_defs
	: let_def ( COMMA! let_def )*
		{ ## = #(#[ATLIST], ##) }
	;

let_def
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"LetDef"], ##) }
	;

with_defs
	: with_def (COMMA! with_def )*
		{ ## = #(#[ATLIST], ##) }
	;

with_def
	: id constructor
		{ ## = #(#[ATAPPL,"WithDef"], ##) }
	;

transf_application
	: transf_construct 
		( RDARROW! id 
			{ ## = #(#[ATAPPL,"Store"], ##) } 
		)?
	;

transf_merge
	:! l:transf_application 
		( n:merge_names r:transf_application
		{ ## = #(#[ATAPPL,"Join"], #l, #r, #n) } 
		|
		{ ## = #l } 
		)
	|! n2:merge_names STAR! o:transf_application
		{ ## = #(#[ATAPPL,"Iterate"], #o, #n2) } 
	;

merge_names
	: merge_union_names merge_opt_isect_names
	|! i:merge_isect_names u:merge_opt_union_names
		
		{ ## = #i }
		{ ##.setNextSibling(#u) }
	;

merge_union_names
	: LSLASH! id_list RSLASH!
	;

merge_isect_names
	: RSLASH! id_list LSLASH!
	;

merge_opt_union_names
	: merge_union_names
	| 
		{ ## = #(#[ATLIST]) }
	;

merge_opt_isect_names
	: merge_isect_names
	| 
		{ ## = #(#[ATLIST]) }
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
		( ( VERT! transf_choice )+
			{ ## = #(#[ATAPPL,"Choice"], #(#[ATLIST],##)) }	
		)?
	;

transf_expr
	: transf_choice
	;

constructor
	: 
		{ ## = #(#[ATAPPL,"Term"], ##) }
	| EQUAL! transf
		{ ## = #(#[ATAPPL,"TermTransf"], ##) }
	| LSQUARE! RSQUARE! 
		( EQUAL! id 
		{ ## = #(#[ATAPPL,"TableCopy"], ##) }
		|
		{ ## = #(#[ATAPPL,"Table"], ##) }
		)
	| LPAREN! RPAREN! ( EQUAL! transf )?
		{ ## = #(#[ATAPPL,"Dynamic"], ##) }
	;

rule
	: term RARROW! term 
		( WHERE! transf_choice
			{ ## = #(#[ATAPPL,"RuleWhere"], ##) }
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
		( ( VERT! anon_rule )+
		{ ## = #(#[ATAPPL,"Choice"], #(#[ATLIST],##)) }
		)?
	;

term
	: term_atom 
		( options { warnWhenFollowAmbig=false; }
		: term_anno
			{ ## = #(#[ATAPPL,"Annos"], ##) }
		)?
	| transf_atom
	;

term_atom
	: INT
		{ ## = #(#[ATAPPL,"Int"], #(#[ATINT],##)) }
	| REAL
		{ ## = #(#[ATAPPL,"Real"], #(#[ATREAL],##)) }
	| STR
		{ ## = #(#[ATAPPL,"Str"], #(#[ATSTR],##)) }
	| LSQUARE! term_list RSQUARE!
	| term_name
		{ ## = #(#[ATAPPL,"ApplName"], ##) }
	| term_tuple
	| term_appl
	| term_appl_cons
	| term_var
		(AT! term 
			{ ## = #(#[ATAPPL,"As"], ##) }
		)?
	| term_wildcard
	| LANGLE! transf RANGLE!
		{ ## = #(#[ATAPPL,"Transf"], ##) }
	;

term_name
	: UID
		{ ## = #(#[ATSTR],##) }
	;

term_var
	: LID
		{ ## = #(#[ATAPPL,"Var"], #(#[ATSTR],##)) }
	;

term_tuple
	: term_args
		{ ## = #(#[ATAPPL,"Appl"], #[ATSTR,""], ##) }
	;
	
term_appl
	: term_name term_args
		{ ## = #(#[ATAPPL,"Appl"], ##) }
	;

term_appl_cons
	: ( term_var | term_wildcard ) LPAREN! term_list RPAREN!
		{ ## = #(#[ATAPPL,"ApplCons"], ##) }
	;
	
term_args
	: LPAREN! ( term ( COMMA! term )* )? RPAREN!
		{ ## = #(#[ATLIST],##) }
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
	: term_args
	|
		{ ## = #(#[ATLIST]) }
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
		{ ## = #(#[ATLIST],##) }
	;

id
	: ( ID | LID | UID ) 
		{ ## = #(#[ATSTR], ##) }
	;

