'''Pretty-printing of intermediate representation code.
'''


header {
import aterm
import walker
}


class PrettyPrinter:

	convert
		: :module
		| :stmt
		| :expr
		;
	
	module
		: _ -> :path(:module_(_), _)
		;

	module_
		: Module(stmts) 
			-> V([I(V(:stmt*(stmts)))])
		;

	stmt
		: _ -> :path(:stmt_(_), _)
		;
	
	stmt_
		: VarDef(type, name, value)
		| FuncDef(type, name, args, body)
			-> D(V([
				H([:type(type), " ", name, "(", :commas(args), ")"]),
				:block(body)
			]))
		| Assign(type, dst, src)
			-> :semi(H([:expr(dst)," ","="," ",:expr(src)]))
		| If(cond, ifTrue, NoStmt)
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
		| Ret(type, NoExpr)
			-> :semi(H([:kw("return")]))
		| Ret(type, value)
			-> :semi(H([:kw("return"), " ", :expr(value)]))
		| Label(name:_str)
			-> D(H([name,":"]))
		| Branch(label)
			-> :semi(H([:kw("goto"), " ", :expr(label)]))
		| Block(stmts)
			-> V(["{",I(V(:stmt*(stmts))),"}"])
		| Break
			-> :semi(:kw("break"))
		| Continue
			-> :semi(:kw("continue"))
		| Asm(opcode, operands) 
			-> :semi(H([:kw("asm"),"(", :commas([:lit(opcode), *:expr*(operands)]), ")"]))
		| :_assertFail("bad statement term")
		;
	
	block
		: _ -> :path(:block_(_), _)
		;
		
	block_
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
		: _ -> :path(:type_(_), _)
		;
	
	type_
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
		| :_assertFail("bad type term")
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
		: _ -> :path(:expr_(_), _)
		;
	
	expr_
		: False 
			-> "FALSE"
		| True 
			-> "TRUE"
		| Lit(type, value:_lit)
			-> :lit(value)
		| Sym(name:_str)
			-> :sym(name)
		| Cast(type, expr)
			-> H(["(", :type(type), ")", " ", :exprP(_,expr)])
		| Unary(op, expr)
			-> H([:op(:unaryOp(op)), :exprP(_,expr)])
		| Binary(op, lexpr, rexpr)
			-> H([:exprP(_,lexpr), " ", :op(:binaryOp(op)), " ", :exprP(_,rexpr)])
		| Cond(cond, texpr, fexpr)
			-> H([:exprP(_,cond), " ", "?", " ", :exprP(_,texpr), " ", ":", " ", :exprP(_,fexpr)])
		| Call(addr, args)
			-> H([:exprP(_,addr), "(", :commas(:expr*(args)), ")"])
		| Addr(addr)
			-> H([:op("&"), :exprP(_,addr)])
		| Ref(expr)
			-> H([:op("*"), :exprP(_,expr)])
		| :_assertFail("bad expression term")
		;

	exprP(child)
		: { self.prec($child) < self.prec($<) }?
			-> :expr(child)
		|
			-> H(["(", :expr(child), ")"])
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

	
	prec
		"""Operator precendence."""
		
		# See http://www.difranco.net/cop2220/op-prec.htm
		
		: False 
			{ $$ = 0 }		
		| True 
			{ $$ = 0 }		
		| Lit(type, value:_lit)
			{ $$ = 0 }		
		| Sym(name:_str)
			{ $$ = 0 }		
		| Cast(type, expr)
			{ $$ = 1 }		
		| Addr(addr)
			{ $$ = 1 }		
		| Ref(expr)
			{ $$ = 1 }		
		| Unary(op, expr)
			-> :unaryOpPrec(op)
		| Binary(op, lexpr, rexpr)
			-> :binaryOpPrec(op)
		| Cond(cond, texpr, fexpr)
			{ $$ = 13 }		
		| Call(addr, args)
			{ $$ = 0 }
		| :_assertFail("bad expression term")
		;

	unaryOpPrec
		: Not 
			{ $$ = 1 }		
		| BitNot(size) 
			{ $$ = 1 }		
		| Neg(type)
			{ $$ = 1 }		
		;

	binaryOpPrec
		: And
			{ $$ = 10 }		
		| Or
			{ $$ = 11 }		

		| BitAnd(size)
			{ $$ = 7 }		
		| BitOr(size)
			{ $$ = 9 }		
		| BitXor(size)
			{ $$ = 8 }		
		| LShift(size)
			{ $$ = 4 }		
		| RShift(size)
			{ $$ = 4 }		
		
		| Plus(type)
			{ $$ = 3 }		
		| Minus(type)
			{ $$ = 3 }		
		| Mult(type)
			{ $$ = 2 }		
		| Div(type)
			{ $$ = 2 }		
		| Mod(type)
			{ $$ = 2 }		
		
		| Eq(type)
			{ $$ = 6 }
		| NotEq(type)
			{ $$ = 6 }
		| Lt(type)
			{ $$ = 5 }
		| LtEq(type)
			{ $$ = 5 }
		| Gt(type)
			{ $$ = 5 }
		| GtEq(type)
			{ $$ = 5 }	
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

	path(t)
		: _
			{
				try:
					p = $t.getAnnotation($!.parse('Path(_)'))
					p = str(p.args.head)
					$$ = $!.make('T("path",_,_)', p, $<)
				except ValueError:
					$$ = $<				
			}
		;
	
	kw
		: s:_str -> T("type", "keyword", s)
		;
		
	op
		: s:_str -> T("type", "operator", s)
		;

	sym
		: s:_str -> T("type", "symbol", s)
		;
				
	lit
		: l:_lit -> T("type", "literal", :repr(l))
		;


	repr
		: s:_int
			{ $$ = $!.makeStr(repr($s.getValue())) }
		| s:_real 
			{ $$ = $!.makeStr(repr($s.getValue())) }
		| s:_str
			{ $$ = $!.makeStr('"' + repr($s.getValue())[1:-1] + '"') }
		;
	

header {
def prettyPrint(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = PrettyPrinter(term.factory)
	box = boxer.convert(term)
	return box

}


# vim:set syntax=python:
