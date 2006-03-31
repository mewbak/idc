'''Intermediate code representation and manipulation.
'''

header {
import aterm
import walker
}

class Checker:
	'''Check the code correcteness.'''

	module
		: Module(stmts:stmt*)
		| :fail
		;
	
	stmt
		: VarDef(:type, :name, :expr)
		| FuncDef(:type, :name, :arg*)
		| Assign(:type, dst:expr, src:expr)
		| If(:expr, true:stmt, false:stmt)
		| While(:expr, :stmt)
		| Ret(:type, :expr)
		| Label(:name)
		| Branch(label:addr)
		| Block(stmts:stmt*)
		| Break
		| Continue
		| NoOp
		| :fail
		;
	
	arg
		: ArgDef(:type, :name)
		;
		
	type
		: Integer(:size, :sign)
		| Float(:size)
		| Char(:size)
		#| String(:size)
		| Pointer(:size,:type)
		| Array(:type)
		| Void
		| :fail
		;
		
	sign
		: Signed
		| Unsigned
		| :fail
		;
	
	expr
		: True
		| False
		| Literal(:type, :value)
		| Symbol(:name)
		| Cast(:type, :expr)
		| Unary(:unaryOp, :expr)
		| Binary(:binaryOp, :expr, expr)
		| Cond(:expr, :expr, :expr)
		| Call(:addr, :expr*)
		| Addr(:expr)
		| Reference(:addr)
		| Register(name)
		| :fail
		;

	addr
		: :expr
		| :fail
		;
	
	unaryOp
		: Not
		| BitNot(:size)
		| Neg(:type)
		| :fail
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

		| :fail
		;

	name	
		: n:_str
		| :fail
		;

	size
		: s:_int
		| :fail
		;

{
	def fail(self, target):
		msg = 'error: %r unexpected\n' % target
		raise Failure, msg
	
}


class PrettyPrinter:

	convert
		: :module
		| :stmt
		;
	
	module
		: Module(stmts) 
			-> V(:stmt(stmts)*)
		;
	
	stmt
		: Label(name) 
			-> H([name,":"])
		| Assembly(opcode, operands) 
			-> H(["asm","(", :string(opcode), H(:prefix(:expr(operands)*, ", ")), ")"])
		;
	
	expr
		: Constant(num) -> :lit2str(num)
		| Register(reg) -> reg
		;
	
	lit2str
		: n { $$ = self.factory.makeStr(str($n.getValue())) }
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
	
	string
		: _ -> H(["\"", _, "\""])
		;


header {
def prettyPrint(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = PrettyPrinter(term.getFactory())
	box = boxer.convert(term)
	return box

}


# vim:set syntax=python:
