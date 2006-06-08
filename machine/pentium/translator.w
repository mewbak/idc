'''Module for handling assembly language code.'''

# TODO: redesign this module in order to cope with more than one machine

header {

from ssl.pentium import insn_table

opcode_table = {
	"orl": "OR.RMOD",
	"xorl": "XOR.RMOD",
	"leal": "LEA.OD",
	"imull": "IMUL.OD",
	"idivb": "IDIV",
	"idivw": "IDIV.AX",
	"idivl": "IDIV.EAX",
	"pushl": "PUSH.OD",
	"popl": "POP.OD",
	"leave": "LEAVE",
}

}


class Translator:

{
	tmp_no = 0
}	
	module
		: Module(stmts)
			{
				res = []
				for astmt in $stmts:
					tmp = self.stmt(astmt)
					for stmt in tmp:
						res.append(stmt)
				$$ = $!.make("Module(_)", res)
			}
		;
	
	stmt
		: Asm("ret", [])
			-> [Ret(Void, NoExpr)]
		| Asm(opcode:_str, operands:_list)
			{
				op = $opcode.getValue()
				try:
					op = opcode_table[op]
				except KeyError:
					op = op.upper()
				try:
					params, temps, pattern = insn_table[op]
				except KeyError:
					return [$<]

				res = []
				kargs = {}
				for param, operand in zip(params, $operands):
					kargs[param] = operand
				for temp in temps:
					self.tmp_no += 1
					name = "tmp%d" % self.tmp_no
					kargs[temp] = $!.make("Sym(_)", name)

				res = $!.make(pattern, **kargs)
				$$ = res
			}
		| _ 
			-> [_]
		;
