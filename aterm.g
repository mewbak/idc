header {
}

header "atermParser.__main__" {
    from aterm import Factory
    from atermLexer import Lexer

    factory = Factory()
    lexer = Lexer()
    parser = Parser(lexer, factory = factory)
    t = parser.term()
    print t
}

header "atermParser.__init__" {
    self.factory = kwargs["factory"]
}

options {
	language  = "Python";
}

class atermLexer extends Lexer;
options {
}

tokens {
	INT;
	REAL;
}

// Whitespace -- ignored
WS	: (' '|'\t'|'\f')+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n') { $newline; $setType(SKIP); }
	;

REAL_OR_INT	
	: { $setType(INT); }
		('-')? // sign
		(
			('0'..'9')+ ( '.' ('0'..'9')* { $setType(REAL); } )?
			| '.' ('0'..'9')+ { $setType(REAL); }
		) // fraction
		( ('e'|'E') ('-'|'+')? ('0'..'9')+ { $setType(REAL); } )? // exponent
	;

STR	: '"'! (STRCHAR)* '"'!;

protected
STRCHAR: ESCCHAR
	| ~('"'|'\\')
	;

protected
ESCCHAR	: '\\'!
		( 'n' { $setText("\n"); }
		| 'r' { $setText("\r"); }
		| 't' { $setText("\t"); }
		| '"' { $setText("\""); }
		| ~('n'|'r'|'t'|'"')
		)
	;

CONS: ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'*'|'+'|'-')* ;
VAR: ('a'..'z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'*'|'+'|'-')* ;
WILDCARD: '_';

COMMA	: ',';

LPAREN	: '(';
RPAREN	: ')';
LSQUARE	: '[';
RSQUARE	: ']';
LCURLY	: '{';
RCURLY	: '}';

STAR	: '*';

class atermParser extends Parser;
options {
}

start returns [res]
	: t=aterm EOF { res = t }
	;

aterm returns [res]
	: term=term 
		( 
			{ res = term }
		| LCURLY anno=aterms RCURLY
			{ res = term.setAnnotation(anno) }
 		)
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
	| 
		( cname:CONS
			{ res = self.factory.makeCons(cname.getText()) }	
		| vname:VAR 
			{ res = self.factory.makeVar(vname.getText()) }
		| WILDCARD 
			{ res = self.factory.makeWildcard() }
		)	
		(
		| LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		)
	;

aterms returns [res]
	:
		{ res = self.factory.makeNilList() }
	| head=term
		(
			{ res = self.factory.makeConsList(head) }
		| COMMA tail=aterms
			{ res = self.factory.makeConsList(head, tail) }
		)
	| STAR
		(
			{ res = self.factory.makeWildcard() }
		| vname:VAR
			{ res = self.factory.makeVar(vname.getText()) }
		)
	;