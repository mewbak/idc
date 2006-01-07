header {
}

header "atermParser.__main__" {
    import aterm
    from atermLexer import Lexer
	
    lexer = Lexer()
    parser = Parser(lexer)
    t = parser.aterm()
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

NAME	: ('a'..'z'|'A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'*'|'+'|'-')* ;

COMMA	: ',';

LPAREN	: '(';
RPAREN	: ')';
LSQUARE	: '[';
RSQUARE	: ']';
LANGLE	: '<';
RANGLE	: '>';
LBRACKET	: '{';
RBRACKET	: '}';

class atermParser extends Parser;
options {
}

start returns [res]
	: t=aterm EOF { res = t }
	;

aterm returns [res]
	: t=term 
		( 
			{ res = t }
		| a=annotation 
			{ res = t.setAnnotation(a) }
 		)
	;

term returns [res]
	: ival:INT
		{ res = self.factory.makeInt(int(ival.getText())) }
	| rval:REAL
		{ res = self.factory.makeReal(float(rval.getText())) }
	| sval:STR
		{ res = self.factory.makeStr(sval.getText()) }
	| name:NAME
		( 
			{ res = self.factory.makeAppl(name.getText()) }
		| LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(name.getText(), args) }
		)
	| LSQUARE elms=aterms RSQUARE
		{ res = elms }
	| LANGLE pat=aterm RANGLE
		{ res = self.factory.makePlaceholder(pat) }
	;

annotation returns [res]
	: RBRACKET a=aterms LBRACKET { res = a }
	;

aterms returns [res]
	:
		{ res = self.factory.makeEmpty() }
	| head=aterm
		( 
			{ res = self.factory.makeList(head) }
		| COMMA tail=aterms
			{ res = self.factory.makeList(head, tail) }
		)
	;

