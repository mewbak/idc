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
		| NoStmt
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


# vim:set syntax=python:
