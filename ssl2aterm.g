// ANTLR grammar for the Semantics Specification Language (SSL)
//
// Based on:
// - citeseer.ist.psu.edu/cifuentes98specifying.html
// - sslscanner.l and sslparser.y from UQBT source distribution.
// - sslscanner.l and sslparser.y from boomerang source distribution.

header {

from sslParser import SemanticException

}

header "ssl2aterm.__main__" {
    from sslLexer import Lexer
    from sslParser import Parser
    from sslPreprocessor import Walker as Preprocessor
    from aterm import Factory

    lexer = Lexer()

    parser = Parser(lexer)
    parser.start()
    ast = parser.getAST()

    preprocessor = Preprocessor()
    preprocessor.start(ast)
    ast = preprocessor.getAST()
	print ast
	
    factory = Factory()
    walker = Walker(factory)
    walker.start(ast)
}

header "ssl2aterm.__init__" {
    self.factory = args[0]
    self.registers = {}
    self.instructions = {}
    self.locals = [{}]
}

options {
    language = "Python";
}

{
opTable = {
    LNOT: "Not",
    LAND: "And",
    LOR: "Or",

    NOT: "BitNot(size)",
    AND: "BitAnd(size)",
    OR: "BitOr(size)",
    XOR: "BitOr(size)",

    EQ: "Eq(Integer(size,sign))",
    NE: "NotEq(Integer(size,sign))",
    LT: "Lt(Integer(size,Signed))",
    GT: "Gt(Integer(size,Signed))",
    LE: "LtEq(Integer(size,Signed))",
    GE: "GtEq(Integer(size,Signed))",
    LTU: "Lt(Integer(size,Unsigned))",
    GTU: "Gt(Integer(size,Unsigned))",
    LEU: "LtEq(Integer(size,Unsigned))",
    GEU: "GtEq(Integer(size,Unsigned))",

    //NEG: "Neg(Integer(size, Signed))",
    PLUS: "Plus(Integer(size,sign))",
    MINUS: "Minus(Integer(size,sign))",
    MUL: "Mult(Integer(size,Unsigned))",
    DIV: "Div(Integer(size,Unsigned))",
    MOD: "Mod(Integer(size,Unsigned))",
    SMUL: "Mult(Integer(size,Signed))",
    SDIV: "Div(Integer(size,Signed))",
    SMOD: "Mod(Integer(size,Signed))",

    FNEG: "Neg(Float)",
    MUL_F: "Mult(Float)",
    MUL_FD: "Mult(Float)",
    MUL_FQ: "Mult(Float)",
    MUL_FSD: "Mult(Float)",
    MUL_FDQ: "Mult(Float)",
    DIV_F: "Mult(Float)",
    DIV_FD: "Mult(Float)",
    DIV_FQ: "Mult(Float)",
    PLUS_F: "Plus(Float)",
    PLUS_FD: "Plus(Float)",
    PLUS_FQ: "Plus(Float)",
    MINUS_F: "Minus(Float)",
    MINUS_FD: "Minus(Float)",
    MINUS_FQ: "Minus(Float)",
}

}

class ssl2aterm extends TreeParser;
options {
    importVocab = ssl;
}

start
	: specification
    ;

specification
	: #(SEMI ( part )*)
    ;

part
	: #(INSTR iname:NAME iparams=param_list ibody=rtl)
		{
            print #iname.getText(), iparams
            print ibody
		}
	| .
    ;

param_list! returns [res]
	: #(COMMA { res = [] } ( n:NAME { res.append(n.getText()) } )* )
    ;

rtl returns [res]
	: #( RTL
			{ res = [] }
        ( t=rt
			{ res.extend(t) }
        )*
      )
			{ res = self.factory.make("Block(_)", res) }
    ;

rt returns [res]
	: #(s:ASSIGNTYPE v=lvalue e=expr)
		{ print "*" }
		{ res = [self.factory.make("Assign(Integer(s),v,e)",
            s = int(#s.getText()[1:-1]),
            v = v,
            e = e)]
		}
    ;

var returns [res]
		{ res = self.factory.make("Unsupported") }
	: r:REG_ID
		{ res = self.factory.make("Symbol(_)", #r.getText()[1:]) }
	| #(ri:REG_IDX i=expr)
		{ raise SemanticException(#ri, "register indexes not supported") }
	| #(mi:MEM_IDX i=expr)
		{ res = self.factory.make("Reference(_)", i) }
//    | t:TEMP
	| v:NAME
		{
            try:
                res = self.locals[-1][#v.getText()]
            except KeyError:
                res = self.factory.make("Symbol(_)", #v.getText())
		}
    ;

lvalue returns [res]
	: v=var 
		{ res = v }
	| #(a:AT var l:expr r:expr)
		{ raise SemanticException(#a, "unsupported") }
	| #(p:PRIME var)
		{ raise SemanticException(#p, "unsupported") }
	;

num returns [res]
	: n:NUM
		{ res = int(#n.getText()) }
	| PLUS l=num r=num
		{ res = l + r }
	| MINUS l=num r=num
		{ res = l - r }
	;

expr returns [res]
		{ res = self.factory.make("Unsupported") }
	: n:NUM
		{ res = self.factory.make("Literal(Integer,_)", int(#n.getText())) }
	| f:FLOATNUM
		{ res = self.factory.make("Literal(Float,_)", float(#f.getText())) }
	| v=var 
		{ res = v }
	| #(AT e=expr l=num r=num)
		{
            res = e
            if l != 0:
                res = self.factory.make("LShift(expr,Literal(Integer,bits))", expr=res, bits=l)
            res = self.factory.make("BitAnd(expr,Literal(Integer,mask))", expr=res, mask=2**r-1)
		}
	| #( QUEST c=expr t=expr f=expr)
		{ res = self.factory.make("Quest(_,_,_)", c, t, f) }
	| #( BUILTIN b:NAME
			{ res = [] }
        ( e=expr
			{ res.append(e) }
        )*
			{ res = self.factory.makeList(res) }
      )
	| #(LCURLY e=expr n=num)
		{ res = self.factory.make("Cast(Integer(size,Unsigned),expr)", expr=e, size=n) }
	| #( o:.
			{
                print "%d:%d" % (#o.getLine(), #o.getColumn())
				
                op = opTable[#o.getType()]
                op = self.factory.make(op, type="Integer", size=32, sign="Unsigned")
			}
		l=expr
		( 
			{
                res = self.factory.make("Unary(_,_)", op, l)
			}
		| r=expr
			{
                res = self.factory.make("Binary(_,_,_)", op, l, r)
			}
		)
	 )
    ;
