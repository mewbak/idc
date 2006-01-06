header {
import aterm
}

header "atermParser.__main__" {
// parser test program
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

AFUN	: ('a'..'z'|'A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'*'|'+'|'-')*
	| '"'! (AFUNCHAR)* '"'!;

protected
AFUNCHAR: ESCCHAR
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

protected
INT	: ('-')? ('0'..'9')+;

protected
REAL	: INT '.' ('0'..'9')+ ( ('e'|'E') INT )?;

REAL_OR_INT
	: ( INT '.' )  => REAL { $setType(REAL); }
	| INT                  { $setType(INT); }
	;

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
	| sym:AFUN
		( 
			{ res = self.factory.makeAppl(sym.getText()) }
		| LPAREN args=aterms RPAREN
			{ res = self.factory.makeAppl(sym.getText(), args) }
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

