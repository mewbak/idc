header {
import sys
}

header "asmParser.__main__" {
    from asmLexer import Lexer
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
       import ir
       import box
       text = box.box2text(ir.ir2box(term))
       print "** C pretty-print **"
       print text
       print
    except box.Failure:
       pass
}

header "asmParser.__init__" {
    self.factory = kwargs["factory"]
}

options {
    language  = "Python";
}

class asmLexer extends Lexer;
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

class asmParser extends Parser;
options {
	buildAST=true;
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
	: (symbol COLON) => (lbl=symbol COLON^ lbls=labels)
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
		{ res = [] }
	| insn=prefixed_instruction
		{ res = [insn] }
	;

prefixed_instruction returns [res]
	: (instruction) => insn=instruction
		{ res = insn }
	| INSTRUCTION insn=instruction
		{ res = insn }
	;

instruction returns [res]
		{ operands = [] }
	: opcode:INSTRUCTION^ (o=operand { operands.append(o) } (COMMA! o=operand  { operands.append(o) })* )?
		{
            res = self.factory.make("Assembly(opcode, operands)", opcode=opcode.getText().lower(), operands=operands)
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
	: PERCENTAGE^ reg=symbol
		{ ret = self.factory.make("Register(reg)", reg=reg) }
	;

memory returns [ret]
	: disp=constant 
		(
		{ ret = self.factory.make("Address()") }
		| LPAR! (base=register)? (COMMA! (index=register)? (COMMA! (scale=integer)? )? )? RPAR!
		{ ret = self.factory.make("Address()") }
		)
	| LPAR! (base=register)? (COMMA! (index=register)? (COMMA! (scale=integer)? )? )? RPAR!
		{ ret = self.factory.make("Address()") }
	;

constant returns [ret] 
	: sym=symbol
		{ ret = self.factory.make("Symbol(sym)", sym=sym) }
	| value=integer
		{ ret = self.factory.make("Constant(value)", value=value) }
	;

symbol returns [name]
	: 
		( d:DIRECTIVE 
			{ name = d.getText() }
		| i:INSTRUCTION
			{ name = i.getText() }
		)
	;

integer returns [value]
	:
		( b:BINARY
			{ value = int(b.getText()[2:], 2) }
		| o:OCTAL 
			{ value = int(o.getText(), 8) }
		| d:DECIMAL
			{ value = int(d.getText()) }
		| h:HEXADECIMAL
			{ value = int(h.getText()[2:], 16) }
		| MINUS^ i=integer
			{ value = -i }
		) 
	;
