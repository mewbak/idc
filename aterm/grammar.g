// Grammar for term parsing


header "parser.__init__" {
    self.factory = kwargs["factory"]
}

options {
	language = "Python";
}


class lexer extends Lexer;

tokens {
	INT;
	REAL;
}

// Whitespace -- ignored
WS	
	: ( ' ' | '\t' | '\f' )+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n' ) { $newline; $setType(SKIP); }
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

CONS
	: ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
	;

VAR
	: ('a'..'z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
	;

WILDCARD: '_';

LPAREN: '(';
RPAREN: ')';

LSQUARE: '[';
RSQUARE: ']';

COMMA: ',';

STAR: '*';

LCURLY: '{';
RCURLY: '}';

ASSIGN: '=';


class parser extends Parser;

options {
	defaultErrorHandler = false;
}

all returns [res]
	: res=aterm EOF
	;

aterm returns [res]
	: res=term 
		( options { greedy = true; }: LCURLY anno=aterms RCURLY
			{ res = res.setAnnotation(anno) }
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
		{ res = self.factory.makeNilList() }
	|
		head=aterm 
		( COMMA tail=aterms 
		|
			{ tail = self.factory.makeNilList() }
		)
		{ res = self.factory.makeConsList(head, tail) }
	|
		STAR
			{ res = self.factory.makeWildcard() }
		( vname:VAR
			{ res = self.factory.makeVar(vname.getText(), res) }
		)?
	;
