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

tokens {
	INT;
	REAL;
}

// Whitespace -- ignored
WS	: ( ' ' | '\t' | '\f' )+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n') { $newline; $setType(SKIP); }
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

CONS: ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* ;
VAR: ('a'..'z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* ;
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
	| LPAREN args=aterms RPAREN
		{ res = self.factory.makeAppl(self.factory.makeStr(""), args) }
	| cname:CONS
		{ res = self.factory.makeStr(cname.getText()) }
		( LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		|
			{ res = self.factory.makeAppl(res) }
		)
		
	|
		( vname:VAR
			{ res = self.factory.makeVar(vname.getText()) }
		| WILDCARD 
			{ res = self.factory.makeWildcard() }
		)	
		( LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		)?
	;

aterms returns [res]
	:
		{ res = self.factory.makeNilList() }
	| aterms=aterms_rest
		{ res = aterms }
	;
	
aterms_rest returns [res]
	: head=aterm
		(
			{ res = self.factory.makeConsList(head) }
		| COMMA tail=aterms_rest
			{ res = self.factory.makeConsList(head, tail) }
		)
	| STAR
		( ( WILDCARD )?
			{ res = self.factory.makeWildcard() }
		| vname:VAR
			{ res = self.factory.makeVar(vname.getText()) }
		)
	;
