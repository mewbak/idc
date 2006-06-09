header {
import sys
}

header "att_parser.__main__" {
    from att_lexer import Lexer
    from aterm import Factory
    
    factory = Factory()
    lexer = Lexer()
    parser = Parser(lexer, factory = factory)
    term = parser.start()
    
    print "** ANTLR AST **"
    ast = parser.getAST()
    print ast.toStringList()
    print

    print "** Aterm AST **"
    print str(term)
    print

    try:
        from transf.exception import Failure
        from ir import pprint
        from box import stringify
       
        text = stringify(pprint.module(term))
        print "** C pretty-print **"
        print text
        print
    except Failure:
        pass
}

header "att_parser.__init__" {
    self.factory = kwargs["factory"]
}

options {
    language  = "Python";
}

class att_lexer extends Lexer;
options {
	k = 2;
}

DIRECTIVE: '.' ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'0'..'9')*;

INSTRUCTION: ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'0'..'9')*;





BINARY: '0' ('b'|'B')! ('0'|'1')*;
HEXADECIMAL: '0' ('x'|'X') ('0'..'9'|'a'..'f'|'A'..'F')*;
OCTAL: '0' ('0'..'9')*;
DECIMAL: '1'..'9' ('0'..'9')*;

// TODO: float point numbers

PERCENTAGE: '%';
DOLLAR: '$';
COMMA: ',';
COLON: ':';
AT: '@';

LPAR: '(';
RPAR: ')';


MINUS: '-';

PLUS: '+';

CHAR
	:	'\'' (ESC|~'\'') '\''
	;

STRING
	:	'"' (ESC|~'"')* '"'
	;

protected
ESC	:	'\\'
		(	'n'
		|	'r'
		|	't'
		|	'b'
		|	'f'
		|	'"'
		|	'\''
		|	'\\'
		|	'0'..'3'
			(
				options {
					warnWhenFollowAmbig = false;
				}
			:	'0'..'9'
				(
					options {
						warnWhenFollowAmbig = false;
					}
				:	'0'..'9'
				)?
			)?
		|	'4'..'7'
			(
				options {
					warnWhenFollowAmbig = false;
				}
			:	'0'..'9'
			)?
		)
	;


// Whitespace -- ignored
WS  :
        (   ' '
        |   '\t'
        |   '\f'
        )
        { $setType(SKIP); }
    ;

EOL
    :
        (   "\r\n"  // DOS
        |   '\r'    // Macintosh
        |   '\n'    // Unix
        )
        { $newline; }
    ;

// Single-line comments
SL_COMMENT
	:	"#"
		(~('\n'|'\r'))* ('\n'|'\r'('\n')?)?
		{ $newline; $setType(SKIP); }
	;

// multiple-line comments
//ML_COMMENT
// 	:	"/*"
// 		(	
// 			{ LA(2)!='/' }? '*'
// 		|	'\r' '\n'		{newline();}
// 		|	'\r'			{newline();}
// 		|	'\n'			{newline();}
// 		|	~('*'|'\n'|'\r')
// 		)*
// 		"*/"
// 		{$setType(Token.SKIP);}
// 	;

class att_parser extends Parser;
options {
	buildAST=true; // TODO: remove -- only used for debugging
	k = 3;
}

start returns [res]
		{ insns = [] }
	:
		( s=statement
			{ insns.extend(s) } 
		)* EOF
		{ res = self.factory.make("Module(insns)", insns = insns) }
	;

statement returns [res]
	: lbls=labels isns=tail EOL
		{
            res = []
            res.extend(lbls)
            res.extend(isns)
		}
 	;

labels returns [res]
	: ( symbol COLON ) => (lbl=symbol COLON^ lbls=labels)
		{
            res = [self.factory.make("Label(lbl)", lbl=lbl)]
            res.extend(lbls)
        }
	| /* no label */
		{ res = [] }
	;

tail returns [res]
	: /* empty statement */
		{ res = [] }
	| DIRECTIVE^ (~EOL)*
		// FIXME: Do not ignore directives
		{ res = [] }
	| insn=prefixed_instruction
		{ res = [insn] }
	;

prefixed_instruction returns [res]
	: ( instruction ) => insn=instruction
		{ res = insn }
	| INSTRUCTION insn=instruction
		// FIXME: Do not ignore instruction prefixes
		{ res = insn }
	;

instruction returns [res]
		{ operands = [] }
	: opcode:INSTRUCTION^ ( o=operand { operands.append(o) } ( COMMA! o=operand { operands.append(o) } )* )?
		{
            // have destination operand as first
			operands.reverse()
            res = self.factory.make("Asm(_, _)", #opcode.getText().lower(), operands)
		}
	;
 
operand returns [res]
	: o=register
		{ res = o }
	| o=immediate
		{ res = o }
	| o=memory
		{ res = o }
	;

immediate returns [ret]
	: DOLLAR^ c=constant
		{ ret = c }
	;

register returns [ret]
	: PERCENTAGE^ name=symbol
		{ ret = self.factory.make("Sym(_)", name) }
	;

memory returns [ret]
		{
            disp = None
            base = None
		}
	: ( disp=constant ( base=memory_base )? | base=memory_base )
		{
            if base is None:
                addr = disp
            elif disp is None:
                addr = base
            else:
                addr = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", base, disp)
            ret = self.factory.make("Ref(_)", addr)
		}
	;

memory_base returns [ret]
		{
            base = None
            index = None
            scale = 1
		}
	: LPAR! (base=register)? ( COMMA! (index=register)? ( COMMA! (scale=integer)? )? )? RPAR!
		{
            if not index is None and scale != 1:
                scale = self.factory.make("Lit(Int(32,Signed),_))", scale)
                index = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", index, scale)
            if base is None:
                ret = index
            elif index is None:
                ret = base
            else:
                ret = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", base, index)
		}
	;

constant returns [ret] 
	: sym=symbol
		{ ret = self.factory.make("Sym(_)", sym) }
	| value=integer
		{ ret = self.factory.make("Lit(Int(32,Signed),_)", value) }
	;

symbol returns [name]
	: 
		( d:DIRECTIVE 
			{ name = #d.getText() }
		| i:INSTRUCTION
			{ name = #i.getText() }
		)
	;

integer returns [value]
	:
		( b:BINARY
			{ value = int(#b.getText()[2:], 2) }
		| o:OCTAL 
			{ value = int(#o.getText(), 8) }
		| d:DECIMAL
			{ value = int(#d.getText()) }
		| h:HEXADECIMAL
			{ value = int(#h.getText()[2:], 16) }
		| MINUS^ i=integer
			{ value = -i }
		) 
	;
