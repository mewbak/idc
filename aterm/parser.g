// Aterm parser


header {
    from aterm.factory import factory
    from aterm import match
    from aterm import build
}

options {
	language = "Python";
}


class parser extends Parser;

options {
	defaultErrorHandler = false;
}

do_term returns [res]
	: res=term EOF
	;

term returns [res]
	: res=term_atom
		( options { greedy = true; }
		: LCURLY annos=term_list RCURLY
			{ res = res.setAnnotations(annos) }
		)?
	;

term_atom returns [res]
	: ival:INT
		{ res = factory.makeInt(int(ival.getText())) }
	| rval:REAL
		{ res = factory.makeReal(float(rval.getText())) }
	| sval:STR
		{ res = factory.makeStr(sval.getText()) }
	| LSQUARE elms=term_list RSQUARE
		{ res = elms }
	| LPAREN args=term_list RPAREN
		{ res = factory.makeAppl(factory.makeStr(""), args) }
	| 
		( cname:CONS
			{ res = factory.makeStr(cname.getText()) }
		| vname:VAR
			{ res = factory.makeStr(vname.getText()) }
		| WILDCARD
			{ res = factory.makeStr("_") }
		) 
		( LPAREN args=term_list RPAREN
			{ res = factory.makeAppl(res, args) }
		|
			{ res = factory.makeAppl(res) }
		)
	;

term_list returns [res]
	:
		{ res = factory.makeNil() }
	| head=term 
		( COMMA tail=term_list 
		|
			{ tail = factory.makeNil() }
		)
		{ res = factory.makeCons(head, tail) }
	| STAR
		(
			{ res = factory.makeStr("_") }
		| vname:VAR
			{ res = factory.makeStr(vname.getText()) }
		)
			{ res = factory.makeAppl(res) }
	;
	
do_match_term returns [res]
	: res=match_term EOF
	;

match_term returns [res]
	: res=match_term_atom 
		( options { greedy = true; }
		: LCURLY annos=match_term_list RCURLY 
		)?
	;

match_term_atom returns [res]
	: ival:INT
		{ res = match.Int(int(ival.getText())) }
	| rval:REAL
		{ res = match.Real(float(rval.getText())) }
	| sval:STR
		{ res = match.Str(sval.getText()) }
	| LSQUARE elms=match_term_list RSQUARE
		{ res = elms }
	| LPAREN args=match_term_args RPAREN
		{ res = match.Appl("", args) }
	| cname:CONS
			{ name = cname.getText() }
		( LPAREN args=match_term_args RPAREN
		| 
			{ args = [] } 
		)
			{ res = match.Appl(name, args) }
	| WILDCARD 
			{ res = match.Wildcard() }
		( LPAREN args=match_term_list RPAREN
			{ res = match.ApplCons(res, args) }
		)?
	| vname:VAR
			{ res = match.Var(vname.getText()) }
		( ASSIGN pattern=match_term
			{ res = match.Seq(pattern, res) }
		| LPAREN args=match_term_list RPAREN
			{ res = match.ApplCons(res, args) }
		)?
	;
	
match_term_list returns [res]
	:
		{ res = match.Nil() }
	| head=match_term 
		( COMMA tail=match_term_list 
		| 
			{ tail = match.Nil() } 
		)
			{ res = match.Cons(head, tail) }
	| STAR		
		( 
			{ res = match.Wildcard() }
		| vname:VAR
			{ res = match.Var(vname.getText()) }
		)
	;

match_term_args returns [res]
	: ( arg=match_term 
			{ res = [arg] }
		( COMMA arg=match_term 
			{ res.append(arg) }
		)* 
	  )? 
	;

do_build_term returns [res]
	: res=build_term EOF
	;

build_term returns [res]
	: res=build_term_atom 
		( options { greedy = true; }
		: LCURLY annos=build_term_list RCURLY 
			{ res = build.Annos(annos) }
		)?
	;

build_term_atom returns [res]
	: ival:INT
		{ res = build.Int(int(ival.getText())) }
	| rval:REAL
		{ res = build.Real(float(rval.getText())) }
	| sval:STR
		{ res = build.Str(sval.getText()) }
	| LSQUARE elms=build_term_list RSQUARE
		{ res = elms }
	| LPAREN args=build_term_args RPAREN
		{ res = build.Appl("", args) }
	| cname:CONS
			{ name = cname.getText() }
		( LPAREN args=build_term_args RPAREN
		| 
			{ args = () } 
		)
			{ res = build.Appl(name, args) }
	| WILDCARD 
			{ res = build.Wildcard() }
		( LPAREN args=build_term_list RPAREN
			{ res = build.ApplCons(res, args) }
		)?
	| vname:VAR
			{ res = build.Var(vname.getText()) }
		( LPAREN args=build_term_list RPAREN
			{ res = build.ApplCons(res, args) }
		)?
	;
	
build_term_list returns [res]
	:
		{ res = build.Nil() }
	| head=build_term 
		( COMMA tail=build_term_list 
		| 
			{ tail = build.Nil() } 
		)
			{ res = build.Cons(head, tail) }
	| STAR		
		( 
			{ res = build.Wildcard() }
		| vname:VAR
			{ res = build.Var(vname.getText()) }
		)
	;

build_term_args returns [res]
	: ( arg=build_term 
			{ res = [arg] }
		( COMMA arg=build_term 
			{ res.append(arg) }
		)* 
	  )? 
	;
