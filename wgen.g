/* 
 * Grammar for generating aterm walkers. See walker.py for more information
 * regarding the walker semantics. The syntax is inspired on ANTLR, Python, and
 * ATerm syntaxes.
 */

header "wgenParser.__init__" {
    self.debug = kwargs.get("debug", False)
}

header "wgenWalker.__init__" {
    self.fp = args[0]
    self.debug = kwargs.get("debug", False)
}

options {
	language = "Python";
}


class wgenLexer extends Lexer;

options {
	k = 3;
	testLiterals = false;
}

tokens {
	HEADER = "header";
	CLASS = "class";
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
	: ( ' ' | '\t' | '\f' | EOL )+ 
		{ $setType(SKIP); }
	;

COMMENT
    : 
		"#" 
		( ~('\n'|'\r') )*
		EOL
			{ $setType(SKIP); }
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
options {generateAmbigWarnings = false;}
    : "'''" (options {greedy = false;}: ESC | EOL | . )* "'''"
    | "\"\"\"" (options {greedy = false;}: ESC | EOL | . )* "\"\"\""
	| '\'' ( ESC | ~'\'' )* '\''
	| '"' ( ESC | ~'"' )* '"'
	;

protected
ESC
    :   '\\' ( EOL | . )
    ;

CONS
options { testLiterals = true; }
    : ('A'..'Z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
    ;
VAR
options { testLiterals = true; }
    : ('a'..'z') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')* 
    ;

TRANSF
	: '_'! ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
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

// FIXME: don't do this in the lexer, but in the walker, see
// http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475109
protected
ACTION_INTERPOLATION
	:
		'$'!
		( ('a'..'z') ( options { warnWhenFollowAmbig=false; } : 'a'..'z'|'A'..'Z'|'0'..'9'|'_')*
			{ text = "_k['%s']" % $getText }
		| ( options { warnWhenFollowAmbig=false; } : '0'..'9')+
			{ text = "_[%s]" % $getText }
	    | '$'
			{ text = "_r" }
	    | '#'
			{ text = "_n" }
	    | '<'
			{ text = "_t" }
		)
			{ $setText(text) }
	;
	
protected
NESTED_ACTION
    :
        ( '{' NESTED_ACTION '}'
        | COMMENT
        | STR
        | EOL
        | ACTION_INTERPOLATION
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
	NIL;
}

grammar
	: 
		( docstring )? 
		( headr
		| walker 
		)* 
		EOF!
	;

headr
	: HEADER^ ACTION
	;

walker
	:
		CLASS^ id ( LPAREN! id RPAREN! )? COLON!
		( docstring )?
		( ACTION 
		| rule 
		)*
	;

rule
	:
		id args
		( docstring )?
		( ACTION )?
		COLON! block SEMI!
		{ ## = #(#[RULE,"RULE"], ##) }
	;

docstring
	: STR
	;

args
	: LPAREN^ ( arg ( COMMA! arg )* )? RPAREN!
	|
		{ ## = #(#[LPAREN,"("]) }
	;

arg
	: id
	| ACTION
	;
	
block
	: alternative ( OR! alternative )*
	;

alternative
	: ( predicate )* ( INTO ( production )* )?
		{ ## = #(#[ALTERNATIVE,"ALTERNATIVE"], ##) }
	;

predicate
	: ( SEMPRED ) => SEMPRED
	| ( ACTION ) => ACTION
	| debug_term
	;

production
	: ( ACTION ) => ACTION
	| debug_term
	;

debug_term
	: t:term
		{
            if self.debug:
                import sys
                sys.stderr.write("*** Term ***\n")
                sys.stderr.write(#t.toStringTree())
                sys.stderr.write("\n")
		}
	;

// TODO: support variable assignments
term
	: INT^
	| REAL^
	| STR^
	| LSQUARE! term_list RSQUARE!
		{ ## = #(#[LIST,"LIST"], ##) }
	| LPAREN! term_list RPAREN!
		{ ## = #(#[APPL,"APPL"], #[CONS,""], ##) }
	| CONS opt_args
		{ ## = #(#[APPL,"APPL"], ##) }
	|
		( VAR | WILDCARD )
		( (LPAREN) => LPAREN! term_list RPAREN!
			{ ## = #(#[APPL,"APPL"], ##) }	
		)?
	| TRANSF^ 
		( ( LPAREN ) => LPAREN! ( term ( COMMA! term )* )? RPAREN! )?
		( STAR^ )?
	| ACTION^
	;

opt_args
	: (LPAREN) => LPAREN! term_list RPAREN!
	| nil
	;
	
nil
	:
		{ ## = #(#[NIL,"NIL"]) }	
	;

term_list
	: nil
	| term ( COMMA! term_list | nil )
		{ ## = #(#[COMMA,","], ##) }	
	| STAR! opt_wildcard
	;
	
opt_wildcard
	: term
	|
		{ ## = #(#[WILDCARD,"_"]) }	
	;

id
	: CONS
	| VAR
	| TRANSF
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

	def dedent(self):
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
	:
		( docstring )?
			{
                self.writeln("from walker import Walker, Failure")
                self.writeln()
            }
		(part)*
	;

docstring
	: s:STR
		{
            self.writeln(#s.getText())
            self.writeln()
		}
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
        ( docstring )?
		( ( method )+
		|
			{
                self.writeln("pass")
            }
		)
			{
                self.dedent()
                self.writeln()
            }
	  )
	;

id returns [ret]
	: u:CONS { ret = #u.getText() }
	| l:VAR { ret = #l.getText() }
	| d:TRANSF { ret = #d.getText() }
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
		n=id args:LPAREN
			{
                self.writeln()
                self.writeind()
                
                self.write("def %s(self, _t" % n)
                self.declare_args(#args)
                self.write("):")
                self.writeeol()
                self.indent()
			}
        ( docstring )?
			{
                self.writeln("_f = self.factory")
                self.import_args(#args)
            }
		( action )?
		( alternative )+
		    {
                self.writeln()
                self.writeln("raise Failure")
                self.dedent()
		    }
	  )
	;

declare_args
		{ ret = [] } 
	: #(LPAREN ( declare_arg )* )
	;
	
declare_arg
		{ self.write(", ") }
	: n=id
		{ self.write(n) }
	| a:ACTION
		{ self.write(#a.getText()) }
	;

import_args
		{ self.writeln("_a = {}") } 
	: #(LPAREN ( import_arg )* )
	;
	
import_arg
	: n=id
		{ self.writeln("_a['%s'] = %s" % (n, n)) }
	| a:ACTION
	;

alternative
	: #(
		ALTERNATIVE
			{
                self.writeln("try:")
                self.indent()
                self.writeln("_r = _t")
                self.writeln("_ = []")
                self.writeln("_k = _a.copy()")
			}
		( predicate )+
		( INTO ( production )+ )?
			{
                self.writeln("return _r")
                self.dedent()
                self.writeln("except Failure:")
                self.indent()
                self.writeln("pass")
                self.dedent()
            }
	  )
	;

predicate
	: ( ACTION ) => action
	| ( SEMPRED ) => p:SEMPRED 
	        {
                self.writeln("if not (%s):" % p)
                self.indent()
                self.writeln("raise Failure")
                self.dedent()
	        }
	| pattern=t:stringify_term
	        {
                self.writeln("if not _f.match(%r, _t, _, _k):" % pattern)
                self.indent()
                self.writeln("raise Failure")
                self.dedent()
                if not self.is_static_term(#t):
                    self.argn = 0
                    self.post_match_term(#t)
                    self.writeln("_r = _f.make(%r, *_, **_k)" % pattern)
	        }
	;

production
	: ( ACTION ) => action
	| flag=t:is_static_term
		{
            if flag:
                pattern = self.stringify_term(#t)
                self.writeln("_r = _f.make(%r, *_, **_k)" % pattern)
            else:
                self.argn = 0
                pattern = self.build_term(#t)
                self.writeln("_r = %s" % pattern)
        }
	;

is_static_term returns [ret]
	: ( INT | REAL | STR | CONS | VAR | WILDCARD )
		{ ret = True }
	| #( LIST ret=is_static_term )
	| #( APPL c=is_static_term a=is_static_term  )
		{ ret = c and a }
	| TRANSF 
		{ ret = False }
	| ACTION
		{ ret = False }
	| NIL
		{ ret = True }
	| #( COMMA h=is_static_term t=is_static_term )
		{ ret = h and t }
	| #( STAR ret=is_static_term )
	;

stringify_term returns [ret]
	: i:INT 
		{ ret = #i.getText() }
	| r:REAL 
		{ ret = #r.getText() }
	| s:STR 
		{ ret = #s.getText() }
	| c:CONS 
		{ ret = #c.getText() }
	| v:VAR 
		{ ret = #v.getText() }
	| w:WILDCARD 
		{ ret = "_" }
	| #( LIST l=stringify_term_list )
		{ ret = "[%s]" % l }
	| #( APPL c=stringify_term a=stringify_term_list )
		{ ret = "%s(%s)" % (c, a) }
	| TRANSF
		{ ret = "_" }
	| ACTION
		{ ret = "_" }
	| STAR
		{ ret = "_" }
	;

stringify_term_list returns [ret]
	: NIL
		{ ret = "" }
	| #( COMMA h=stringify_term t=stringify_term_list )
		{ ret = ("%s,%s" % (h, t)).rstrip(",") }
	| WILDCARD
		{ ret = "*" }
	| v:VAR 
		{ ret = "*" + #v.getText() }
	;

post_match_term
	: INT | REAL | STR | CONS | VAR
	| WILDCARD 
		{ self.argn += 1 }
	| #( LIST post_match_term )
	| #( APPL post_match_term post_match_term )
	| t:TRANSF // TODO: handle args
		{
            self.writeln("_[%i] = self.%s(_[%i])" % (self.argn, #t.getText(), self.argn))
            self.argn += 1
		}
	| a:ACTION
		{
            self.writeln("_n = %s " % self.argn)
            self.writeln("_[%i] = %s" % (self.argn, #a.getText()))
            self.argn += 1
		}
	| NIL
	| #( COMMA post_match_term post_match_term )
	| #( STAR t2:TRANSF /* TODO: handle args */ )
		{
            self.writeln("_[%i] = self.map(_[%i], self.%s)" % (self.argn, self.argn, #t2.getText()))
            self.argn += 1
		}
	;

build_term returns [ret]
	: i:INT 
		{ ret = "_f.makeInt(%s)" % #i.getText() }
	| r:REAL 
		{ ret = "_f.makeReal(%s)" % #r.getText() }
	| s:STR 
		{ ret = "_f.parse(%r)" % #s.getText() }
	| c:CONS 
		{ ret = "_f.makeStr(%r)" % #c.getText() }
	| v:VAR 
//		{ ret = "_f.makeVar(%r,_f.makeWildcard())" % #v.getText() }
		{ ret = "_k[%r]" % #v.getText() }
	| w:WILDCARD 
//		{ ret = "_f.makeWildcard()" }
		{
            ret = "_[%d]" % self.argn
            self.argn += 1
        }
	| #( LIST l=build_term )
		{ ret = l }
	| #( APPL c=build_term a=build_term )
		{ ret = "_f.makeAppl(%s,%s)" % (c, a) }
	| #( t:TRANSF a=build_trnsf_args)
		{ ret = "self.%s(%s)" % (#t.getText(), a) }
	| a:ACTION
		{ ret = #a.getText() }
	| NIL
		{ ret = "_f.makeNilList()" }
	| #( COMMA h=build_term t=build_term )
		{ ret = "_f.makeConsList(%s,%s)" % (h, t) }
    | #( STAR #( t2:TRANSF ah=build_term at=build_trnsf_args ) )
		{ ret = "self.map(%s,self.%s,%s)" % (ah, #t2.getText(), at) }
	;

build_trnsf_args returns [ret]
	:
		{ ret = "" } { sep = "" }
	 	( t=build_term
		{ ret += sep + t } { sep = "," }
		)*
	;
