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


header {
class Expr:
	'''Utility class for simplify coding of expressions using the builtin operators.'''
	
	def __init__(self, term):
		self.term = term
		self.factory = term.factory
		
		self.sign = self.factory.make("Unknown")
		self.size = self.factory.makeInt(32)
		self.type = self.factory.make("Int(size,sign)", size=self.size, sign=self.sign)
		
	def _make(self, pattern, *args, **kargs):
		return Expr(self.term.factory.make(pattern, *args, **kargs))
	
	def _cast(self, other):
		if isinstance(other, Expr):
			return other
		if isinstance(other, aterm.Term):
			return Expr(other)
		if isinstance(other, int):
			return self._make("Lit(Int(size,sign),value)",
				size = self.size,
				sign = self.sign,
				value = other
			)		
		if isinstance(other, float):
			# FIXME: size
			return self._make("Lit(Float(size),value)",
				size = self.size,
				sign = self.sign,
				value = other
			)
		else:
			raise TypeError, "don't know how to handle '%r'" % other

	_un_op_table = {
		'neg': 'Neg(size)',
		'invert': 'BitNot(size)',
	}
		
	_bin_op_table = {
		'add': 'Plus(type)',
		'sub': 'Minus(type)',
		'mul': 'Mult(type)',
		'div': 'Div(type)',
		'mod': 'Mod(type)',

		'and': 'BitAnd(size)',
		'xor': 'BitXor(size)',
		'or': 'BitOr(size)',
		'lshift': 'LShift(size)',
		'rshift': 'RShift(size)',
	}
	
	def __getattr__(self, name):
		if name.startswith('__') and name.endswith('__'):
			op = name[2:-2]
			if op in self._un_op_table:
				op = self.factory.make(self._un_op_table[op], type = self.type, size = self.size, sign = self.sign)
				return lambda: self._make("Unary(op,expr)", op = op, expr=self.term)
			if op in self._bin_op_table:
				op = self.factory.make(self._bin_op_table[op], type = self.type, size = self.size, sign = self.sign)
				return lambda other: self._make("Binary(op,lexpr,rexpr)", op = op, lexpr=self.term, rexpr=self._cast(other).term)
			if op.startswith('r'):
				op = op[1:]
				if op in self._bin_op_table:
					op = self.factory.make(self._bin_op_table[op], type = self.type, size = self.size, sign = self.sign)
					return lambda other: self._make("Binary(op,lexpr,rexpr)", op = op, rexpr=self.term, lexpr=self._cast(other).term)
		
		raise AttributeError, "attribute not found '%r'" % name
}
	
	
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
			-> H(["(", :type(type), ")", " ", :exprP(_,expr)])
		| Unary(op, expr)
			-> H([:unaryOp(op), :exprP(_,expr)])
		| Binary(op, lexpr, rexpr)
			-> H([:exprP(_,lexpr), " ", :binaryOp(op), " ", :exprP(_,rexpr)])
		| Cond(cond, texpr, fexpr)
			-> H([:exprP(_,cond), " ", "?", " ", :exprP(_,texpr), " ", ":", " ", :exprP(_,fexpr)])
		| Call(addr, args)
			-> H([:exprP(_,addr), "(", :commas(:expr*(args)), ")"])
		| Addr(addr)
			-> H([:op("*"), :exprP(_,addr)])
		| Ref(expr)
			-> H([:op("&"), :exprP(_,expr)])
		| :_fatal("bad expression term")
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
		| :_fatal("bad expression term")
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
