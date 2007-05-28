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

atom
	: QUEST! term
		{ ## = #(#[ATAPPL,"Match"], ##) }
	| BANG! term
		{ ## = #(#[ATAPPL,"Build"], ##) }
	| TILDE! term
		{ ## = #(#[ATAPPL,"Congruent"], ##) }
	;

transf
	: transf_expr
	;

transf_atom
	: atom
	| IDENT!
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	| FAIL!
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	| LCURLY! transf RCURLY!
	| LPAREN! transf RPAREN!
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
		{ ## = #(#[ATAPPL,"Transf"], ##) }
	| id LPAREN! args RPAREN!
		{ ## = #(#[ATAPPL,"Macro"], ##) }
	| id EQUAL! transf_atom
		{ ## = #(#[ATAPPL,"Assign"], ##) }
	;

args
	: ( arg ( COMMA! arg )* )?
		{ ## = #(#[ATLIST], ##) }
	;

arg
	: ( transf ) => transf
	| ( INT | REAL | STR | OBJ )
		{ ## = #(#[ATAPPL,"Obj"], #(#[ATSTR],##)) }
	| PRIME! id ( PRIME! )?
		{ ## = #(#[ATAPPL,"Var"], ##) }
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

transf_build_apply
	: transf_atom
		( (term ~EQUAL) => term
			{ ## = #(#[ATAPPL,"BuildApply"], ##) }
		)?
	;

transf_rule
	: (term RARROW!) => term RARROW! term
		{ ## = #(#[ATAPPL,"Rule"], ##) }
	| transf_build_apply
	;

transf_apply_match
	: transf_rule
		( RDARROW! term
			{ ## = #(#[ATAPPL,"ApplyMatch"], ##) }
		)*
	;

transf_merge
	:! l:transf_apply_match
		( n:merge_names r:transf_apply_match
			{ ## = #(#[ATAPPL,"Join"], #l, #r, #n) }
		|
			{ ## = #l }
		)
	|! n2:merge_names STAR! o:transf_apply_match
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
	: (term RARROW! term WHERE!) => term RARROW! term WHERE! transf_composition
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
	: atom
	| term_atom
		( LCURLY! term_list RCURLY!
			{ ## = #(#[ATAPPL,"Annos"], ##) }
		)?
	| term_var AT! term
		{ ## = #(#[ATAPPL,"As"], ##) }
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
//	| term_args
//		{ ## = #(#[ATAPPL,"Appl"], #[ATSTR,""], ##) }
	| term_name term_args
		{ ## = #(#[ATAPPL,"Appl"], ##) }
	| ( term_var | term_wildcard ) LPAREN! term_list RPAREN!
		{ ## = #(#[ATAPPL,"ApplCons"], ##) }
	| term_var
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

term_args
	: LPAREN! ( term ( COMMA! term )* )? RPAREN!
		{ ## = #(#[ATLIST],##) }
	;

term_wildcard
	: WILDCARD!
		{ ## = #(#[ATAPPL,"Wildcard"]) }
	;

term_list
	: term_implicit_nil
	| term ( COMMA! term_list | term_implicit_nil )
		{ ## = #(#[ATAPPL,"Cons"], ##) }
	| STAR! term_opt_wildcard
	;

term_implicit_nil
	:
		{ ## = #(#[ATAPPL,"Nil"]) }
	;

term_opt_wildcard
	: term
	| term_implicit_wildcard
	;

term_implicit_wildcard
	:
		{ ## = #(#[ATAPPL,"Wildcard"]) }
	;

id_list
	: ( id ( COMMA! id )* )?
		{ ## = #(#[ATLIST],##) }
	;

id
	: ( ID | LID | UID )
		{ ## = #(#[ATSTR], ##) }
	;

