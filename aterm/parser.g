// Aterm parser


header "parser.__init__" {
    self.factory = kwargs["factory"]
}

options {
	language = "Python";
}


class parser extends Parser;

options {
	defaultErrorHandler = false;
}

tokens {
	INT;
	REAL;
	STR;
	CONS;
	WILDCARD;
	VAR;
	LPAREN;
	RPAREN;
	LSQUARE;
	RSQUARE;
	LCURLY;
	RCURLY;
	COMMA;
	STAR;
	ASSIGN;
}

all returns [res]
	: res=aterm EOF
	;

aterm returns [res]
	: res=term 
		( options { greedy = true; }: LCURLY anno=aterms RCURLY
			{ res = res.setAnnotations(anno) }
		)?
	;

term returns [res]
	: ival:INT
		{ res = self.factory.makeInt(int(ival.getText())) }
	| rval:REAL
		{ res = self.factory.makeReal(float(rval.getText())) }
	| sval:STR
		{ res = self.factory.makeStr(sval.getText()) }
	| LSQUARE elms=aterms RSQUARE
		{ res = elms }
	| LPAREN args=aterms RPAREN
		{ res = self.factory.makeAppl(self.factory.makeStr(""), args) }
	| 
		cname:CONS
			{ res = self.factory.makeStr(cname.getText()) }
		( LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		|
			{ res = self.factory.makeAppl(res) }
		)
	| 
		WILDCARD 
			{ res = self.factory.makeWildcard() }
		( LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		)?
	| 
		vname:VAR
		(
			{ res = self.factory.makeVar(vname.getText(), self.factory.makeWildcard()) }
		| ASSIGN pattern=aterm
			{ res = self.factory.makeVar(vname.getText(), pattern) }
		| LPAREN args=aterms RPAREN
			{ res = self.factory.makeVar(vname.getText(), self.factory.makeWildcard()) }
			{ res = self.factory.makeAppl(res, args) }
		)
	;

aterms returns [res]
	:
		{ res = self.factory.makeNil() }
	|
		head=aterm 
		( COMMA tail=aterms 
		|
			{ tail = self.factory.makeNil() }
		)
		{ res = self.factory.makeCons(head, tail) }
	|
		STAR
			{ res = self.factory.makeWildcard() }
		( vname:VAR
			{ res = self.factory.makeVar(vname.getText(), res) }
		)?
	;
