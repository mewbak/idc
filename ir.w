'''Intermediate code representation and manipulation.
'''

header {
import aterm
import walker
}

class Checker:
	'''Check the code correctness.'''

	module
		: Module(stmts:stmt*)
		;
	
	stmt
		: VarDef(:type, :name, :expr)
		| FuncDef(:type, :name, :arg*)
		| Assign(:type, dst:expr, src:expr)
		| If(cond:expr, ifTrue:stmt, ifFalse:stmt)
		| While(cond:expr, :stmt)
		| Ret(:type, :expr)
		| Label(:name)
		| Branch(label:addr)
		| Block(stmts:stmt*)
		| Break
		| Continue
		| NoOp
		;
	
	arg
		: ArgDef(:type, :name)
		;
		
	type
		: Void
		| Bool
		| Int(:size, :sign)
		| Float(:size)
		| Char(:size)
		| Pointer(:size,:type)
		| Func(:type, :type*)
		| Array(:type)
		| Compound(:type*)
		| Union(:type*)
		| Blob(:size)
		;
		
	sign
		: Signed
		| Unsigned
		| Unknown
		;
	
	expr
		: True
		| False
		| Lit(:type, :value)
		| Sym(:name)
		| Cast(:type, :expr)
		| Unary(:unaryOp, :expr)
		| Binary(:binaryOp, :expr, expr)
		| Cond(:expr, onTrue:expr, onFalse:expr)
		| Call(:addr, args:expr*)
		| Addr(:expr)
		| Ref(:addr)
		;

	addr
		: :expr
		;
	
	unaryOp
		: Not
		| BitNot(:size)
		| Neg(:type)
		;

	binaryOp
		: And
		| Or
		
		| BitAnd(:size)
		| BitOr(:size)
		| BitXor(:size)
		| LShift(:size)
		| RShift(:size)
		
		| Plus(:type)
		| Minus(:type)
		| Mult(:type)
		| Div(:type)
		| Mod(:type)
		
		| Eq(:type)
		| NotEq(:type)
		| Lt(:type)
		| LtEq(:type)
		| Gt(:type)
		| GtEq(:type)

		;

	name	
		: n:_str
		;

	size
		: s:_int
		;


class PrettyPrinter:

	convert
		: :module
		| :stmt
		;
	
	module
		: Module(stmts) 
			-> V(:stmt*(stmts))
		;

	stmt
		: VarDef(type, name, value)
		| FuncDef(type, name, args)
		| Assign(type, dst, src)
			-> :semi(H([:expr(dst)," ","="," ",:expr(src)]))
		| If(cond, ifTrue, NoOp)
			-> V([
				H([:kw("if"),"(",:expr(cond),")"]),
				:block(ifTrue)
			])
		| If(cond:expr, ifTrue, ifFalse)
			-> V([
				H([:kw("if"),"(",:expr(cond),")"]),
				:block(ifTrue),
				:kw("else"),
				:block(ifFalse)
			])
		| While(cond, stmt)
			-> V([
				H([:kw("while"),"(",:expr(cond),")"]),
				:block(stmt)
			])
		| Ret(type, value)
			-> :semi(H([:kw("return"), " ", :expr(value)]))
		| Label(name:_str)
			-> H([name,":"])
		| Branch(label)
			-> :semi(H([:kw("goto"), " ", :expr(label)]))
		| Block(stmts)
			-> V(["{",I(V(:stmt*(stmts))),"}"])
		| Break
			-> :semi(:kw("break"))
		| Continue
			-> :semi(:kw("continue"))
		| Asm(opcode, operands) 
			-> :semi(H([:kw("asm"),"(", :commas([:repr(opcode), *:expr*(operands)]), ")"]))
		| :_fatal("bad statement term")
		;
	
	block
		: Block(stmts) 
			-> V(["{",I(V(:stmt*(stmts))),"}"])
		| stmt 
			-> V([I(:stmt(stmt))])
		;
		
	semi
		: stmt -> H([stmt, ";"])
		;
		
	arg
		: ArgDef(:type, :name)
		;

	type
		: Int(size, sign)
			-> H([:sign(sign), " ", :integerSize(size)])
		| Float(32)
			-> :kw("float")
		| Float(64)
			-> :kw("float")
		| Char(size)
			-> :kw("char")
		| Pointer(size,type) 
			-> H([:type(type), " ", "*"])
		| Array(type)
			-> H([:type(type), "[", "]"])
		| Void
			-> :kw("void")
		| :_fatal("bad type term")
		;
	
	# TODO: at some point these names must be derived from architecture specs
	integerSize
		: 8 -> :kw("char")
		| 16 -> H([:kw("short"), " ", :kw("int")])
		| 32 -> :kw("int")
		| 64 -> H([:kw("long"), " ", :kw("int")])
		| n:_int -> H(["int", :repr(n)])
		;
	
	sign
		: Signed -> :kw("signed")
		| Unsigned -> :kw("unsigned")
		;
		
	expr
		: False 
			-> "FALSE"
		| True 
			-> "TRUE"
		| Lit(type, value:_lit)
			-> :repr(value)
		| Sym(name:_str)
			-> name
		| Cast(type, expr)
			-> H(["(", "(", :type(type), ")", " ", "(", :expr(expr), ")", ")"])
		| Unary(op, expr)
			-> H([:unaryOp(op), "(", :expr(expr), ")"])
		| Binary(op, lexpr, rexpr)
			-> H(["(", :expr(lexpr), ")", :binaryOp(op), "(", :expr(rexpr), ")"])
		| Cond(cond, texpr, fexpr)
			-> H(["(", :expr(cond), "?", :expr(texpr), ":", :expr(fexpr), ")"])
		| Call(addr, args)
			-> H([:expr(addr), "(", :commas(:expr*(args)), ")"])
		| Addr(addr)
			-> H([:op("*"), "(", :expr(addr), ")"])
		| Ref(expr)
			-> H([:op("&"), "(", :expr(expr), ")"])
		| :_fatal("bad expression term")
		;

	unaryOp
		: Not -> "!"
		| BitNot(size) -> "~"
		| Neg(type) -> "-"
		;

	binaryOp
		: And -> "&&"
		| Or -> "||"

		| BitAnd(size) -> "&"
		| BitOr(size) -> "|"
		| BitXor(size) -> "^"
		| LShift(size) -> "<<"
		| RShift(size) -> ">>"
		
		| Plus(type) -> "+"
		| Minus(type) -> "-"
		| Mult(type) -> "*"
		| Div(type) -> "/"
		| Mod(type) -> "%"
		
		| Eq(type) -> "=="
		| NotEq(type) -> "!="
		| Lt(type) -> "<"
		| LtEq(type) -> "<="
		| Gt(type) -> ">"
		| GtEq(type) -> ">="
		;

	name
		: n:_str
		;

	size
		: s:_int
		;

	commas
		: l:_list -> H(:join(l, ", "))
		;

	join(s)
		: [] -> []
		| [h] -> [h]
		| [h, *t] -> [h, *:prefix(t, s)]
		;
	
	prefix(p)
		: [] -> []
		| [h, *t] -> [p, h, *:prefix(t, p)]
		;
	
	kw
		: s:_str
		;
		
	op
		: s:_str
		;

	repr
		: s:_int
			{ $$ = self.factory.makeStr(repr($s.getValue())) }
		| s:_real 
			{ $$ = self.factory.makeStr(repr($s.getValue())) }
		| s:_str
			{ $$ = self.factory.makeStr('"' + repr($s.getValue())[1:-1] + '"') }
		;
	

header {
def prettyPrint(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = PrettyPrinter(term.getFactory())
	box = boxer.convert(term)
	return box

}


# vim:set syntax=python:
