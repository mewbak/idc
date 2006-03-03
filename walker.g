// Grammer for aterm walkers.
// It is inspired on ANTLR, Python and ATerm syntaxes.

header {
    import sys
}

header "walkerWalker.__init__" {
    self.fp = args[0]
}

options {
	language  = "Python";
}


class walkerLexer extends Lexer;

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
        "#" 
        ( ~('\n'|'\r') )*
        EOL
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
	: '"' ( '\\' . | ~'"' )* '"'
	| '\'' ( '\\' . | ~'\'' )* '\''
	;

UCID
    options { testLiterals = true; }
    : ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
    ;
LCID
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

ACTION
	: '{'! NESTED_ACTION '}'! ( '?'! { $setType(SEMPRED) } )?
	;

DOT
	: '.'
	;

protected
NESTED_ACTION
    :
        ( '{' NESTED_ACTION '}'
        | COMMENT
        | STR
        | EOL
        | ~'}'
        )*
    ;



class walkerParser extends Parser;

options {
	k=2;
	buildAST = true;
}

tokens {
	ALTERNATIVE;
	APPL;
	LIST;
	ARG;
	TRANSF;
}

grammar
	: ( part )* EOF!
	;

part
	: HEADER^ ACTION
	| CLASS^ id ( LPAREN! id RPAREN! )? COLON! ( method )*
	;

method
	: ACTION
	| rule
	;

rule
	:
		id ( args )?
		( ACTION )?
		COLON! block SEMI!
		{ ## = #(#[RULE,"RULE"], ##) }
	;

args
	: LPAREN^ ( arg ( COMMA! arg )* )? RPAREN!
	;

arg
	: ( STAR ( STAR )? )? id
		{ ## = #(#[ARG,"ARG"], ##) }
	;
	
block
	: alternative ( OR! alternative )*
	;

alternative
	: ( p:SEMPRED )* term (element)*
		{ ## = #(#[ALTERNATIVE,"ALTERNATIVE"], ##) }
	;

element
	: p:SEMPRED^
	| INTO^ term
	| a:ACTION^
	;

term
	: INT^
	| REAL^
	| STR^
	| LSQUARE! terms RSQUARE!
		{ ## = #(#[LIST,"LIST"], ##) }
	| LPAREN! terms RPAREN!
		{ ## = #(#[APPL,"APPL"], #[UCID,""], ##) }
	| UCID ( LPAREN! terms RPAREN! )?
		{ ## = #(#[APPL,"APPL"], ##) }
	|
		( LCID | WILDCARD )
		( LPAREN! terms RPAREN!
			{ ## = #(#[APPL,"APPL"], ##) }	
		)?
	| DOT! ( UCID | LCID ) ( LPAREN! terms RPAREN! )?
		{ ## = #(#[TRNSF,"TRNSF"], ##) }	
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
	: UCID			
	| LCID
	;


class walkerWalker extends TreeParser;

{
    _indent = 0
    
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

	def indent(self):
        self._indent += 1

	def deindent(self):
        self._indent -= 1

    def write(self, str):
        self.fp.write(str)
    
    def writeind(self, line=""):
        self.write("\t"*self._indent)
    
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
			{
                self.writeln("from aterm import TransformationFailureException")
                self.writeln("from walker import Walker")
                self.writeln()
            }
	: (part)*
	;

part
	: #( HEADER action )
	| #( CLASS 
		n=id
		( p=id
		|
			{
                p = "Walker"
            }
		)
			{
                self.writeln("class %s(%s):" % (n, p))
                self.indent()
            }
		( ( method )+
		|
			{
                self.writeln("pass")
            }
		)
			{
                self.deindent()
                self.writeln()
            }
	  )
	;

id returns [ret]
	: u:UCID { ret = #u.getText() }
	| l:LCID { ret = #l.getText() }
	;

method
	: action
	| rule
	;

action
	: a:ACTION
		{ self.writeblock(#a.getText()) }
	;

rule
	: #( RULE 
		n=id
			{
                self.writeln()
                self.writeln("def %s(self, src):" % n)
                self.indent()
                self.writeln("retval = src")
            }
		( action )?
		( alternative )+
		    {
                self.writeln()
                self.writeln("raise TransformationFailureException")
                self.deindent()
		    }
	  )
	;

alternative
	: #( ALTERNATIVE
			{
                self.writeln()
                self.writeln("try:")
                self.indent()
                self.writeln("args = []")
                self.writeln("kargs = {}")
			}
		( element )+
			{
                self.writeln("return retval")
                self.deindent()
                self.writeln("except TransformationFailureException:")
                self.indent()
                self.writeln("pass")
                self.deindent()
            }
	  )
	;

element
	:
		( p:SEMPRED 
	        {
                self.writeln("if not (p):" % p)
	        }
	    | match=term
	        {
                pattern, args = match
                self.writeln("if not self.factory.match(%r, src, args, kargs):" % pattern)
                static = True
                for i in range(len(args)):
                    arg = args[i]
                    if arg != "_":
                        static = False
                        self.writeln("args[%i] = self.%s(args[%i])" % (i, arg))
                if not static:
                    self.writeln("retval = self.factory.make(%r, *args, **kargs)" % pattern)
	        }
	    )
	    {
            self.indent()
            self.writeln("raise TransformationFailureException")
            self.deindent()
	    }
	| #( INTO build=term )
		{
            pattern, args = build
            self.writeln("retval = self.factory.make(%r, *args, **kargs)" % pattern)
        }
	| action
	;


term returns [ret]
	: i:INT { ret = #i.getText(), [] }
	| r:REAL { ret = #r.getText(), [] }
	| s:STR { ret = #s.getText(), [] }
	| v:LCID { ret = #v.getText(), [] }
	| w:WILDCARD { ret = "_", ["_"] }
	| #( LIST t=terms )
		{ ret = "[%s]" % (t[0]), t[1] }
	| #( APPL c=cons a=terms )
		{ ret = "%s(%s)" % (c[0], a[0]), c[1] + a[1] }
	| #( TRNSF s=id a=terms )
		{ ret = "_", [s] }
	;

cons returns [ret]
	: s:STR { ret = #s.getText(), [] }
	| c:UCID { ret = #c.getText(), [] }
	| v:LCID { ret = #v.getText(), [] }
	| w:WILDCARD { ret = "_", ["_"] }
	;

terms returns [ret]
		{ ret = [], [] }
	: ( t=term { ret[0].append(t[0]); ret[1].extend(t[1]) } )*
		{ ret = ','.join(ret[0]), ret[1] }
	;