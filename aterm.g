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
REAL	: INT '.' ('0'..'9')+ ( ('e'|'E') INT );

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
	: t=term ( annotation )? { res = t }
	;

term returns [res]
	: ival:INT
		{ res = aterm.ATermInt(int(ival.getText())) }
	| rval:REAL
		{ res = aterm.ATermReal(float(rval.getText())) }
	| sym:AFUN
		( 
			{ res = aterm.ATermAppl(sym.getText()) }
		| LPAREN args=aterms RPAREN
			{ res = aterm.ATermAppl(sym.getText(), args) }
		)
	| LSQUARE elms=aterms RSQUARE
		{ res = aterm.ATermList(elms) }
	| LANGLE pat=aterm RANGLE
		{ res = aterm.ATermPlaceholder(pat) }
	;

annotation
	: RBRACKET a=aterms LBRACKET;


aterms returns [res = []]
	:
	| head=aterm { res.append(head) } (COMMA tail=aterm { res.append(tail) } )*
	;

