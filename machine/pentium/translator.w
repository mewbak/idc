'''Module for handling assembly language code.'''

# TODO: redesign this module in order to cope with more than one machine

header {

from ssl.pentium import insn_table

opcode_table = {
	"andl": "AND.RMOD",
	"orl": "OR.RMOD",
	"xorl": "XOR.RMOD",
	"addl": "ADD.RMOD",
	"subl": "SUB.RMOD",
	"imull": "IMUL.OD",
	"idivb": "IDIV",
	"idivw": "IDIV.AX",
	"idivl": "IDIV.EAX",
	"movl": "MOV.RMOD",
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
			-> [Ret(Void, Sym(" "))]
		| Asm(opcode:_str, operands:_list)
			{
				try:
					params, temps, pattern = insn_table[opcode_table[$opcode.getValue()]]
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
