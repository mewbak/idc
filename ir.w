'''Intermediate code representation and manipulation.
'''

header {
import sys

import aterm
import walker
}

class Checker:
	'''Check the code correcteness.'''

	module
		: Module(_stmt*)
		#| fail
		;
	
	stmt
		: VarDef(_type, _name, _expr)
		| FuncDef(_type, _name, _arg*)
		| Assign(_type, _expr, _expr) # dst src
		| If(_expr, _stmt, _stmt)
		| While(_expr, _stmt)
		| Ret(_type, _expr)
		| Label(_name)
		| Branch(_addr) # label
		| Block(_stmt*)
		| NoOp
		| fail
		;
	
	type
		: Integer(_size, _sign)
		| Float(_size)
		| Char(_size)
		#| String(_size)
		| Pointer(_size)
		| Array(_type)
		| fail
		;
		
	sign
		: Signed
		| Unsigned
		| fail
		;
	
	expr
		: True
		| False
		| Literal(_type, _value)
		| Symbol(_name)
		| Cast(_type, _expr)
		| Unary(_unaryOp, _expr)
		| Binary(_binaryOp, _expr, expr)
		| Cond(_expr, _expr, _expr)
		| Call(_addr, _expr*)
		| Addr(_expr)
		| Reference(_addr)
		| Register(name)
		| fail
		;

	addr
		: _expr
		| fail
		;
	
	unaryOp
		: Not
		| BitNot(_size)
		| Neg(_type)
		| fail
		;

	binaryOp
		: And
		| Or
		
		| BitAnd(_size)
		| BitOr(_size)
		| BitXor(_size)
		| LShift(_size)
		| RShift(_size)
		
		| Plus(_type)
		| Minus(_type)
		| Mult(_type)
		| Div(_type)
		| Mod(_type)
		
		| Eq(_type)
		| NotEq(_type)
		| Lt(_type)
		| LtEq(_type)
		| Gt(_type)
		| GtEq(_type)

		| fail
		;

	name	
		: n { $n.getType() == aterm.STR }?
		| fail
		;

	size
		: s  { $n.getType() == aterm.INT }?
		| fail
		;

{
	def fail(self, target, expected):
		msg = 'error: a %s expected, but %r found\n' % (expected.getValue(), target)
		sys.stderr.write(msg)
		raise Failure, msg
	
}
		
		 	


class PrettyPrinter:

	convert
		: _module
		| _stmt
		;
	
	module
		: Module(stmts) -> V(_stmt(stmts)*)
		;
	
	stmt
		: Label(name) -> H([name,":"])
		| Assembly(opcode, operands) -> H(["asm","(", _string(opcode), H(_prefix(_expr(operands)*, ", ")), ")"])
		;
	
	expr
		: Constant(num) -> _lit2str(num)
		| Register(reg) -> reg
		;
	
	lit2str
		: n { $$ = self.factory.makeStr(str($n.getValue())) }
		;
	
	join(s)
		: [] -> []
		| [h] -> [h]
		| [h, *t] -> [h, *_prefix(t, s)]
		;
	
	prefix(p)
		: [] -> []
		| [h, *t] -> [p, h, *_prefix(t, p)]
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
