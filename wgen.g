// Grammer for aterm wgens.
// It is inspired on ANTLR, Python and ATerm syntaxes.

header {
    import sys
}

header "wgenWalker.__init__" {
    self.fp = args[0]
}

options {
	language  = "Python";
}


class wgenLexer extends Lexer;

options {
	k = 2;
	testLiterals=false;
}

tokens {
	HEADER="header";
	CLASS="class";
	DOT;
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
		| '.' { $setType(DOT); } ( ('0'..'9')+ { $setType(REAL); } )?
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


class wgenParser extends Parser;

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
	:
		( SEMPRED
		| ACTION
		)*
		term
		( SEMPRED
		| ACTION
		)*
		( INTO 
			( ACTION )*
			( term )
			( ACTION )*
		)?
		{ ## = #(#[ALTERNATIVE,"ALTERNATIVE"], ##) }
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
		( LCID^ | WILDCARD^ )
		( LPAREN! terms RPAREN!
			{ ## = #(#[APPL,"APPL"], ##) }	
		)?
	| DOT! ( UCID | LCID ) ( LPAREN! terms RPAREN! )?
		{ ## = #(#[TRNSF,"TRNSF"], ##) }	
	;

inner_term
	: term
	|
		ACTION^
		( LPAREN! terms RPAREN!
			{ ## = #(#[APPL,"APPL"], ##) }	
		)?	;

terms
	:
	| terms_rest
	;
	
terms_rest
	: inner_term ( COMMA! terms_rest )?
	| STAR^ ( ( WILDCARD )? | VAR )
	;

id
	: UCID			
	| LCID
	;


class wgenWalker extends TreeParser;

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
                self.writeln("from walker import Walker, TransformationFailureException")
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
                self.writeln("def %s(self, target):" % n)
                self.indent()
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
	: #(
		ALTERNATIVE
			{
                self.writeln("try:")
                self.indent()
                self.writeln("result = target")
                self.writeln("args = []")
                self.writeln("kargs = {}")
			}
		( predicate )+
		( INTO ( production )+ )?
			{
                self.writeln("return result")
                self.deindent()
                self.writeln("except TransformationFailureException:")
                self.indent()
                self.writeln("pass")
                self.deindent()
            }
	  )
	;

predicate
	: ( ACTION ) => action
	| p:SEMPRED 
	        {
                self.writeln("if not (%s):" % p)
                self.indent()
                self.writeln("raise TransformationFailureException")
                self.deindent()
	        }
	| pattern=t:stringify_term
	        {
                self.writeln("if not self.factory.match(%r, target, args, kargs):" % pattern)
                self.indent()
                self.writeln("raise TransformationFailureException")
                self.deindent()
                if not self.is_static_term(#t):
                    self.argn = 0
                    self.post_match_term(#t)
                    self.writeln("result = self.factory.make(%r, *args, **kargs)" % pattern)
	        }
	;

production
	: ( ACTION ) => action
	| flag=t:is_static_term
		{
            if flag:
                pattern = self.stringify_term(#t)
                self.writeln("result = self.factory.make(%r, *args, **kargs)" % pattern)
            else:
                pattern = self.build_term(#t)
                self.writeln("result = %s.make(*args, **kargs)" % pattern)
        }
	;

is_static_term returns [ret]
	: ( INT | REAL | STR | UCID | LCID | WILDCARD ) { ret = True }
	| #( LIST { ret = True } ( e=is_static_term { ret = ret and e } )* )
	| #( APPL ret=is_static_term ( a=is_static_term { ret = ret and a } )* )
	| TRNSF { ret = False }
	;

stringify_term returns [ret]
	: i:INT 
		{ ret = #i.getText() }
	| r:REAL 
		{ ret = #r.getText() }
	| s:STR 
		{ ret = repr(#s.getText()) }
	| v:LCID 
		{ ret = #v.getText() }
	| w:WILDCARD 
		{ ret = "_" }
	| #( LIST l=stringify_term_list)
		{ ret = "[%s]" % l }
	| #( APPL c=stringify_term_cons a=stringify_term_list )
		{ ret = "%s(%s)" % (c, a) }
	| TRNSF
		{ ret = "_" }
	| ACTION
	;

stringify_term_cons returns [ret]
	: s:STR 
		{ ret = #s.getText() }
	| c:UCID 
		{ ret = #c.getText() }
	| v:LCID 
		{ ret = #v.getText() }
	| w:WILDCARD 
		{ ret = "_" }
	;

stringify_term_list returns [ret]
		{ ret = [] }
	: ( t=stringify_term { ret.append(t) } )*
		{ ret = ','.join(ret) }
	;

post_match_term
	: ( INT | REAL | STR | UCID | LCID )
	| w:WILDCARD 
		{ self.argn += 1 }
	| #( LIST ( post_match_term )* )
	| #( APPL ( post_match_term )+ )
	| #( TRNSF n=id )
		{
            self.writeln("args[%i] = self.%s(args[%i])" % (self.argn, n, self.argn))
            self.argn += 1
		}
	| a:ACTION
		{
            self.writeln("argn = %s " % self.argn)
            self.writeln("args[%i] = %s" % (self.argn, #a.getText()))
            self.argn += 1
		}
	;

build_term returns [ret]
	: i:INT 
		{ ret = "self.factory.makeInt(%r)" % #i.getText() }
	| r:REAL 
		{ ret = "self.factory.makeReal(%r)" % #r.getText() }
	| s:STR 
		{ ret = "self.factory.makeStr(%r)" % #s.getText() }
	| c:UCID 
		{ ret = "self.factory.makeStr(%r)" % #c.getText() }
	| v:LCID 
		{ ret = "self.factory.makeVar(%r,self.factory.makeWildcard())" % #v.getText() }
	| w:WILDCARD 
		{ ret = "self.factory.makeWildcard()" }
	| #( LIST l=build_term_list )
		{ ret = l }
	| #( APPL c=build_term a=build_term_list )
		{ ret = "self.factory.makeAppl(%s,%s)" % (c, a) }
	| #( TRNSF n=id a=build_trnsf_args)
		{ ret = "self.%s(target%s)" % (n, a) }
	| a:ACTION
		{ ret = #a.getText() }
	;

build_term_list returns [ret]
	: ( build_term build_term ) => h=build_term t=build_term_list
		{ ret = "self.factory.makeConsList(%s,%s)" % (h, t) }
	| 
		{ ret = "self.factory.makeNilList()" }
	;

build_trnsf_args returns [ret]
	: h=build_term t=build_trnsf_args
		{ ret = ",%s%s" % (h, t) }
	| 
		{ ret = "" }
	;