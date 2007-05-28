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

definitions
	: ( definition )* EOF!
		{ ## = #(#[ATAPPL,"Defs"],#(#[ATLIST], ##)) }
	;

definition
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"TransfDef"], ##) }
	| id LPAREN! id_list RPAREN! EQUAL! transf
		{ ## = #(#[ATAPPL,"MacroDef"], ##) }
	| GLOBAL! id type
		{ ## = #(#[ATAPPL,"VarDef"], ##) }
	;

type
	:
		{ ## = #(#[ATSTR],#[ATSTR,"Term"]) }
	| LSQUARE! RSQUARE!
		{ ## = #(#[ATSTR],#[ATSTR,"Table"]) }
	;

transf
	: transf_expr
	;

common
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

transf_atom
	: common
	| IDENT!
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	| FAIL!
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	| LCURLY! transf RCURLY!
	| LPAREN! transf RPAREN!
	//| LANGLE! transf RANGLE! term
	//	{ ## = #(#[ATAPPL,"BuildApply"], ##) }
	| IF! if_clauses if_else END!
		{ ## = #(#[ATAPPL,"If"], ##) }
	| SWITCH! transf switch_cases switch_else END!
		{ ## = #(#[ATAPPL,"Switch"], ##) }
	| WITH! var_defs IN! transf END!
		{ ## = #(#[ATAPPL,"With"], ##) }
	| LOCAL! id_list IN! transf END!
		{ ## = #(#[ATAPPL,"Local"], ##) }
	| GLOBAL! id_list IN! transf END!
		{ ## = #(#[ATAPPL,"Global"], ##) }
	| REC! id COLON! transf_atom
		{ ## = #(#[ATAPPL,"Rec"], ##) }
	| id
		(
			{ ## = #(#[ATAPPL,"Transf"], ##) }
		| LPAREN! args RPAREN!
			{ ## = #(#[ATAPPL,"Macro"], ##) }
		)
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
	: ELSE! (COLON!)? transf
	|
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	;

var_defs
	: var_def (COMMA! var_def )*
		{ ## = #(#[ATLIST], ##) }
	;

var_def
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"WithDef"], ##) }
	;

transf_rule
	: (term RARROW!) => term RARROW! term
		{ ## = #(#[ATAPPL,"Rule"], ##) }
	| transf_atom
	;

transf_application
	: transf_rule
		( (term ~EQUAL) => term
			{ ## = #(#[ATAPPL,"BuildApply"], ##) }
		| RDARROW! term
			{ ## = #(#[ATAPPL,"ApplyMatch"], ##) }
		| RDDARROW! id
			{ ## = #(#[ATAPPL,"ApplyStore"], ##) }
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

transf_rule_where
	: (term RARROW! term IF!) => term RARROW! term WHERE! transf_composition
		{ ## = #(#[ATAPPL,"RuleWhere"], ##) }
	| transf_composition
	;

transf_choice
	: transf_rule_where
		( AMP! transf_rule_where PLUS! transf_choice
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
	: transf_undeterministic_choice
	;

term
	: term_atom
		( options { warnWhenFollowAmbig=false; }
		: term_anno
			{ ## = #(#[ATAPPL,"Annos"], ##) }
		)?
	| common
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
	//| term_tuple
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

