'''Module for handling assembly language code.'''

# TODO: redesign this module in order to cope with more than one machine

header {
from asmLexer import Lexer
from asmParser import Parser


def load(factory, fp):
	'''Load an assembly file into a low-level IR aterm.'''
	
	lexer = Lexer(fp)
	parser = Parser(lexer, factory = factory)
	term = parser.start()
	return term


def translate(term):
	'''Translate the "Asm" terms into the higher-level IR equivalent 
	constructs by means of the SSL.'''
	
	walker = Translate(term.factory)

	term = walker.module(term)
	
	return term

from pentium import insn_table

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


class Translate:

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
				$$ = self.factory.make("Module(_)", res)
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
					kargs[temp] = self.factory.make("Sym(_)", name)

				res = self.factory.make(pattern, **kargs)
				$$ = res
			}
		| _ 
			-> [_]
		;
	


header {

if __name__ == '__main__':
	import sys
	from aterm import Factory
	factory = Factory()
	term = load(factory, file(sys.argv[1]))
	term = translate(term)
	from ir import PrettyPrinter
	import box
	printer = PrettyPrinter(factory)
	boxes = printer.module(term)
	print box.box2text(boxes)
}
