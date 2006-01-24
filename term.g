header {
}

header "termParser.__main__" {
    from term import Factory
    from termLexer import Lexer

    factory = Factory()
    lexer = Lexer()
    parser = Parser(lexer, factory = factory)
    t = parser.term()
    print t
}

header "termParser.__init__" {
    self.factory = kwargs["factory"]
}

options {
	language  = "Python";
}

class termLexer extends Lexer;
options {
}

// Whitespace -- ignored
WS	: (' '|'\t'|'\f')+ { $setType(SKIP); }
	| ( '\r' ('\n')? | '\n') { $newline; $setType(SKIP); }
	;

protected
INT	: ('-')? ('0'..'9')+;

protected
REAL	: INT '.' ('0'..'9')+ ( ('e'|'E') INT )?;

REAL_OR_INT
	: ( INT '.' ) => REAL { $setType(REAL); }
	| INT                 { $setType(INT); }
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

STAR	: '*';

class termParser extends Parser;
options {
}

start returns [res]
	: t=term EOF { res = t }
	;

term returns [res]
	: ival:INT
		{ res = self.factory.makeInt(int(ival.getText())) }
	| rval:REAL
		{ res = self.factory.makeReal(float(rval.getText())) }
	| sval:STR
		{ res = self.factory.makeStr(sval.getText()) }
	| LSQUARE elms=terms RSQUARE
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
		| LPAREN args=terms RPAREN
			{ res = self.factory.makeAppl(res, args) }
		)
	;

terms returns [res]
	:
		{ res = self.factory.makeNil() }
	| head=term
		(
			{ res = self.factory.makeList(head) }
		| COMMA tail=terms
			{ res = self.factory.makeList(head, tail) }
		)
	| STAR
		(
			{ res = self.factory.makeWildcard() }
		| vname:VAR
			{ res = self.factory.makeVar(vname.getText()) }
		)
	;
