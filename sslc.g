// ANTLR grammar for translating the Semantics Specification Language (SSL)
// into aterms


header {
import sys

import aterm
import ir

from sslLexer import Lexer
from sslParser import Parser, SemanticException
from sslPreprocessor import Walker as Preprocessor

def sslc(fpin, fpout, debug = False):
    lexer = Lexer(fpin)

    parser = Parser(lexer)
    parser.start()
    ast = parser.getAST()

    preprocessor = Preprocessor()
    preprocessor.start(ast)
    ast = preprocessor.getAST()
	
    if debug:
        sys.stderr.write("*** AST begin ***\n")
        sys.stderr.write(ast.toStringList())
        sys.stderr.write("\n")
        sys.stderr.write("*** AST end ***\n")

    factory = aterm.Factory()

    writer = Walker(factory, fpout, debug = debug)
    writer.start(ast)
}

header "sslc.__main__" {
    import optparse
    import os.path

    parser = optparse.OptionParser(
        usage = "\n\t%prog [options] file ...", 
        version = "%prog 1.0")
    parser.add_option(
        "-d", "--debug", 
        action = "store_true", dest = "debug", default = False, 
        help = "show debugging info")
    parser.add_option(
        "-o", "--output", 
        type = "string", dest = "output", 
        help = "specify output file")
    (options, args) = parser.parse_args(sys.argv[1:])

    for arg in args:
        fpin = file(arg, "rt")

        if options.output is None:
            root, ext = os.path.splitext(arg)
            fpout = file(root + ".py", "wt")
        elif options.output is "-":
            fpout = sys.stdout
        else:
            fpout = file(options.output, "wt")

        sslc(fpin, fpout, options.debug)
}

header "sslc.__init__" {
    self.factory = args[0]
    self.fp = args[1]
    self.debug = kwargs.get("debug", False)
    self.registers = {}
    self.instructions = {}
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
    XOR: "BitXor(size)",
    LSHIFT: "LShift(size)",
    RSHIFT: "RShift(size)",
    RSHIFTA: "RShift(size)", // FIXME: handle sign here

    EQ: "Eq(Int(size,sign))",
    NE: "NotEq(Int(size,sign))",
    LT: "Lt(Int(size,Signed))",
    GT: "Gt(Int(size,Signed))",
    LE: "LtEq(Int(size,Signed))",
    GE: "GtEq(Int(size,Signed))",
    LTU: "Lt(Int(size,Unsigned))",
    GTU: "Gt(Int(size,Unsigned))",
    LEU: "LtEq(Int(size,Unsigned))",
    GEU: "GtEq(Int(size,Unsigned))",

    //NEG: "Neg(Int(size,Signed))",
    PLUS: "Plus(Int(size,sign))",
    MINUS: "Minus(Int(size,sign))",
    MUL: "Mult(Int(size,Unsigned))",
    DIV: "Div(Int(size,Unsigned))",
    MOD: "Mod(Int(size,Unsigned))",
    SMUL: "Mult(Int(size,Signed))",
    SDIV: "Div(Int(size,Signed))",
    SMOD: "Mod(Int(size,Signed))",

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

builtinTable = {
    LITERAL_rlc: "rlc",
    LITERAL_rrc: "rrc",
    LITERAL_rl: "rl",
    LITERAL_rr: "rr",
    LITERAL_pow: "pow",
}

}

class sslc extends TreeParser;
options {
    importVocab = ssl;
}

start
	: specification
    ;

specification
	: #( SEMI ( part )* )
		{
            self.fp.write("insn_table = {\n")
            names = self.instructions.keys()
            names.sort()
            for name in names:
                params, temps, body = self.instructions[name]
                self.fp.write("\t%r: (%r, %r, %r),\n" % (name, params, temps, str(body)))
            self.fp.write("}\n")
		}
    ;

part
	: #( INSTR iname:NAME iparams=param_list ibody=r:rtl )
		{
            tmpnames = self.collect_temps(#r)
            
            
            if self.debug:
                sys.stderr.write("*** %s(%s;%s) ***\n" % (#iname.getText(), ",".join(iparams), ",".join(tmpnames)))

            self.instructions[#iname.getText()] = (iparams, tmpnames, ibody)
            
            if self.debug:
           	    from ir import PrettyPrinter
                from box import box2text

                kargs = {}
                for nam in iparams + tmpnames:
                   kargs[nam] = self.factory.make("Sym(_)", nam)
                   
                term = ibody.make(**kargs)
                term = self.factory.make("Block(_)", term)
                
                printer = PrettyPrinter(self.factory)
                text = box2text(printer.stmt(term))
                sys.stderr.write(text)
                sys.stderr.write("\n\n\n")
		}
	| .
		// ignore
    ;

param_list! returns [res]
	: #( COMMA { res = [] } ( n:NAME { res.append(n.getText()) } )* )
    ;

rtl returns [res]
	: #( RTL
			{ res = [] }
        ( t=rt
			{ res.extend(t) }
        )*
      )
			{ res = self.factory.makeList(res) }
    ;

rt returns [res]
		{ res = [] }
	: #( at:ASSIGNTYPE 
		{
            t = #at.getText()[1:-1]
            c = t[0]
            if c.isalpha():
                size = int(t[1:])
                if c == 'i':
                    sign = "Signed"
                    type = "Int(size,sign)"
                elif c == 'j':
                    sign = "Unknown"
                    type = "Int(size,sign)"
                elif c == 'u':
                    sign = "Unsigned"
                    type = "Int(size,sign)"
                elif c == 'f':
                    sign = "Unknown"
                    type = "Float(size)"
                elif c == 'c':
                    sign = "Unknown"
                    type = "Char(size)"
                else:
                    raise SemanticException, "unsupported type code '%s'" % c
            else:
                size = int(t)
                sign = "Unknown"
                if size == 1:
                    type = "Bool"
                else:
                    type = "Blob(size)"
		}
		lv=lvalue e=expr )
		{
            res = [self.factory.make("Assign(_,_,_)",
                self.factory.make(type, size=size, sign=sign),
                lv,
                e)
            ]
		}
	| any:.
		{ raise SemanticException(#any, "unsupported") }
    ;

var returns [res]
		{ res = self.factory.make("Sym(\"UNKNOWN\")") }
	: r:REG_ID
		{ res = self.factory.make("Sym(_)", #r.getText()[1:]) }
	| #( ri:REG_IDX i=expr )
		{ raise SemanticException(#ri, "register indexes not supported") }
	| #( mi:MEM_IDX i=expr )
		{ res = self.factory.make("Ref(_)", i) }
//    | t:TEMP
	| v:NAME
		{ res = self.factory.makeVar(#v.getText(), self.factory.makeWildcard()) }
    ;

lvalue returns [res]
	: v=var 
		{ res = v }
	| #( a:AT v=var l=expr r=expr )
		{ res = v }
		{ raise SemanticException(#a, "unsupported") }
	| #( p:PRIME v=var )
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
		{ res = self.factory.make("Sym(\"UNSUPPORTED_EXPR\")") }
	: n:NUM
		{ res = self.factory.make("Lit(Int(32,Signed),_)", int(#n.getText())) }
	| f:FLOATNUM
		{ res = self.factory.make("Lit(Float(32),_)", float(#f.getText())) }
	| v=var 
		{ res = v }
	| #( AT e=expr 
		( ( num num ) => l=num r=num 
		{
            res = e
            if l != 0:
                res = self.factory.make("Binary(RShift(32),expr,Lit(Int(32,Signed),bits))", expr=res, bits=min(r, l))
            res = self.factory.make("Binary(BitAnd(32),expr,Lit(Int(32,Signed),mask))", 
            	expr=res, 
            	mask= 1 << (abs(l-r)+1) - 1
            )
		}
		| l=expr r=expr
		{
            e = ir.Expr(e)
            l = ir.Expr(l)
            r = ir.Expr(r)
            
            res = (e >> r) & (1 << (l - r + 1) - 1)
            
            res = res.term
		}
		) )
	| #( QUEST c=expr t=expr f=expr )
		{ res = self.factory.make("Cond(_,_,_)", c, t, f) }
	| #( BUILTIN b:NAME args=expr_list )
		{ res = self.factory.make("Call(Sym(_),_)", #b.getText(), args) }
	| #( LCURLY e=expr n=num )
		{ res = self.factory.make("Cast(Int(size,Unsigned),expr)", expr=e, size=n) }
	| #( S_E e=expr )
		// FIXME: handle type and size correctly
		{ res = self.factory.make("Cast(Int(size,Signed),expr)", expr=e, size=32) }
	| #( t:. args=expr_list )
		{
            //print "%d:%d" % (#o.getLine(), #o.getColumn())
            typ = #t.getType()
            if typ in opTable:
                op = opTable[typ]
                op = self.factory.make(op, type="Int", size=32, sign="Signed")
                if len(args) == 1:
                    res = self.factory.make("Unary(_,_)", op, *args)
                elif len(args) == 2:
                    res = self.factory.make("Binary(_,_,_)", op, *args)
                else:
                    raise SemanticException(#t, "bad number of args %i" % len(args))
            else:
                op = builtinTable[typ]
                res = self.factory.make("Call(Sym(_),_)", op, args)
        }
    ;

expr_list returns [res]
	:
		{ res = [] }
        ( e=expr
			{ res.append(e) }
        )*
     ;

collect_temps returns [res]
		{ res = {} }
	: do_collect_temps[res]
		{ res = res.keys() }
	;

do_collect_temps[res]
	: n:NAME
		{
            if #n.getText().startswith("tmp"):
               res[#n.getText()] = None
		}
	| #( . ( do_collect_temps[res] )* )
	;
