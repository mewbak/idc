// Grammer for aterm transformations.
// It is inspired on ANTLR, Python and ATerm syntaxes.

header {
    import sys
}

header "transformationWriter.__main__" {
    from transformationLexer import Lexer
    from transformationParser import Parser

    lexer = Lexer()
    parser = Parser(lexer)
    parser.grammar()
    ast = parser.getAST()
    sys.stderr.write(str(ast))

    writer = Walker()
    writer.start(ast)
}

options {
	language  = "Python";
}


class transformationLexer extends Lexer;

options {
	k = 2;
	testLiterals=false;
}

tokens {
	HEADER="header";
	CLASS="class";
}

protected
EOL
	:
		( '\r'
			( ( '\n' ) => '\n' 
			|
			)
		| '\n'
		)
		{ $newline }
	;
	
// Whitespace -- ignored
WS	
	: ( ' ' | '\t' | '\f' | EOL )+ { $setType(SKIP); }
	;

COMMENT
    :
        ( SL_COMMENT | t:ML_COMMENT { $setType(t.getType()) } )
        {
//            if $getType != DOC_COMMENT:
                $setType(SKIP)
        }
	;

protected
SL_COMMENT
    : 
        "//" 
        ( ~('\n'|'\r') )*
        EOL
	;

protected
ML_COMMENT
    :
        "/*"
        ( { LA(2)!='/' }? '*' { $setType(DOC_COMMENT) }
        |
        )
        (
            options {
                greedy=false;  // make it exit upon "*/"
            }
        :	EOL
        |	~('\n'|'\r')
        )*
        "*/"
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
	: '"'! (STR_CHAR)* '"'!
	;

protected
STR_CHAR
	: ESC_CHAR
	| ~('"'|'\\')
	;

protected
ESC_CHAR	
	:
		'\\'!
		( 'n' { $setText("\n"); }
		| 'r' { $setText("\r"); }
		| 't' { $setText("\t"); }
		| '"' { $setText("\""); }
		| ~('n'|'r'|'t'|'"')
		)
	;

UCASE_ID
    options { testLiterals = true; }
    : ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
    ;
LCASE_ID
    options { testLiterals = true; }
    : ('a'..'z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
    ;

LSQUARE	: '[';
RSQUARE	: ']';

COMMA: ',';

QUESTION: '?';

LPAREN: '(';

RPAREN: ')';

COLON: ':';

STAR: '*';

PLUS: '+';

ASSIGN: '=';

INTO: "->";

SEMI: ';';

CARET: '^';

BANG: '!';

OR: '|';

WILDCARD: '_';

NOT_OP: '~';

RCURLY: '}';

protected
STRING_LITERAL
	: '"' ( ESC | ~'"' )* '"'
	| '\'' ( ESC | ~'\'' )* '\''
	;

protected
ESC
	: '\\' .
	;

ARG_ACTION
    : NESTED_ARG_ACTION
	;

protected
NESTED_ARG_ACTION
    :
        '['
        ( NESTED_ARG_ACTION
        | STRING_LITERAL
        | EOL
        | ~']'
        )*
        ']'
	;

ACTION
	: NESTED_ACTION ( '?'! { $setType(SEMPRED) } )?
	;

protected
NESTED_ACTION
    :
        '{'
        ( NESTED_ACTION
        | COMMENT
        | STRING_LITERAL
        | EOL
        | ~'}'
        )*
        '}'
    ;


class transformationParser extends Parser;

options {
	k=2;
	buildAST = true;
}

tokens {
	ALTERNATIVE;
	APPL;
	LIST;
}

grammar
	:
		( header_
		| class_
		)* 
		EOF!
	;

header_
	: HEADER^ ACTION
	;

class_
	:
		//( DOC_COMMENT )?
        CLASS^ id ( LPAREN! id RPAREN! )? SEMI!
		( method )*
	;

method
	: ACTION
	| rule
	;

rule
	:
		//( DOC_COMMENT )?
		id 
		( ARG_ACTION )?
		( ACTION )?
		COLON! block SEMI!
		{ ## = #(#[RULE,"RULE"], ##) }
	;

block
	: alternative ( OR! alternative )*
	;

alternative
	:
		( p:SEMPRED )?
		term ( INTO term )?
		( a:ACTION )?
		{ ## = #(#[ALTERNATIVE,"ALTERNATIVE"], ##) }
	;

term
	: INT^
	| REAL^
	| STR^
	| LSQUARE! terms RSQUARE!
		{ ## = #(#[LIST,"LIST"], ##) }
	| LPAREN! terms RPAREN!
		{ ## = #(#[APPL,"APPL"], #[UCASE_ID,""], ##) }
	| UCASE_ID ( LPAREN! terms RPAREN! )?
		{ ## = #(#[APPL,"APPL"], ##) }
	|
		( LCASE_ID | WILDCARD )
		( LPAREN! terms RPAREN!
			{ ## = #(#[APPL,"APPL"], ##) }	
		|
		)
	;

terms
	:
	| terms_rest
	;
	
terms_rest
	: term ( COMMA! terms_rest )?
	| STAR^ ( ( WILDCARD )? | VAR )
	;

id
	: UCASE_ID			
	| LCASE_ID
	;


class transformationWriter extends TreeParser;

{
    indent = 0
    
    def stripindent(self, lines):
        // Fix script indentation
        indent = None
        res = []
        for line in lines:
            line = line.rstrip().expandtabs()
            if indent is None:
                if not line:
                    continue
                indent = 0
                while line[indent].isspace():
                    indent += 1
            res.append(line[indent:])
        return res

    def write(self, str):
        sys.stdout.write(str)
    
    def writeind(self, line=""):
        self.write("\t"*self.indent)
    
    def writeeol(self):
        self.write("\n")
    
    def writeln(self, line=""):
        self.writeind()
        self.write(line)
        self.writeeol()
    
    def writeblock(self, str):
        for line in self.stripindent(str.split("\n")):
            self.writeln(line)

}

start
	: (part)*
	;

part
	: #( HEADER action )
	| #( CLASS 
		n=id
		( p=id
			{
                self.writeln("class %s(%s):" % (n, p))
            }
		|
			{
                self.writeln("class %s:" % (n))
            }
		)
			{
                self.indent += 1
            }
		( ( method )+
		|
			{
                self.writeln("pass")
            }
		)
			{
                self.indent -= 1
                self.writeln()
            }
	  )
	;

id returns [ret]
	: u:UCASE_ID { ret = #u.getText() }
	| l:LCASE_ID { ret = #l.getText() }
	;

method
	: action
	| rule
	;

action
	: a:ACTION
		{ self.writeblock(#a.getText()[1:-1]) }
	;

rule
	: #( RULE 
		n=id
			{
                self.writeln()
                self.writeln("def %s(self, src):" % n)
                self.indent += 1
                self.writeln("retval = src")
            }
		( action )?
		( alternative[True] ( alternative[False] )* )?
		    {
                self.writeln("raise Exception")
                self.indent -= 1
		    }
	  )
	;

alternative[first]
	: #( ALTERNATIVE
			{
                self.writeln("args = []; kargs = {}")
                self.writeind()
                self.write("if ")
                first = True
			}
		( p:SEMPRED 
		    {
                if not first:
                    self.write(" and")
                self.write("self.factory.match(%r, src)" % match)
                first = False
		    }
		| match=term
		    {
                if not first:
                    self.write(" and")
                self.write("self.factory.match(%r, src, args, kargs)" % match)
                first = False
		    }
		)*
		    {
                if first:
                    self.write("true")
	                first = False
                self.write(":")
                self.writeeol()
                first = False
                self.indent += 1
		    }	
		( INTO build=term 
			{
                self.writeln("retval = self.factory.make(%r, args, kargs)" % build)
            }
		| action
		)*
			{
                self.writeln("return retval")
                self.indent -= 1
                self.writeln()
            }
	 )
	;



term returns [ret]
	: i:INT { ret = #i.getText() }
	| r:REAL { ret = #r.getText() }
	| s:STR { ret = #s.getText() }
	| v:LCASE_ID { ret = #v.getText() }
	| w:WILDCARD { ret = #w.getText() }
	| #( LIST t=terms )
		{ ret = "[%s]" % (t) }
	| #( APPL c=cons a=terms )
		{ ret = "%s(%s)" % (c, a) }
	;

cons returns [ret]
	: s:STR { ret = #s.getText() }
	| c:UCASE_ID { ret = #c.getText() }
	| v:LCASE_ID { ret = #v.getText() }
	| w:WILDCARD { ret = #w.getText() }
	;

terms returns [ret]
		{ ret = [] }
	: ( t=term { ret.append(t) } )*
		{ ret = ','.join(ret) }
	;