'''Pretty-printing of aterm code using boxes as an intermediate representation,
allowing to easily support several frontend languages and backend formats.

See
http://www.cs.uu.nl/wiki/Visser/GenerationOfFormattersForContext-freeLanguages
about the Box language, upon this code is lossely based.
'''

header {
import aterm
import walker
}


class Ir2Box:

	convert
		: .module
		| .stmt
		;
	
	module
		: Module(stmts) -> V(.map(stmts, {self.stmt}), 1)
		;
	
	stmt
		: Label(name) -> H([name,":"], 0)
		| Assembly(opcode, operands) -> H(["asm","(", .string(opcode), H(.prefix(.map(operands, {self.expr}), ", "), 0), ")"], 0)
		;
	
	expr
		: Constant(num) -> .lit2str(num)
		| Register(reg) -> reg
		;
	
	lit2str
		: n { $$ = self.factory.makeStr(str($n.getValue())) }
		;
	
	join(s)
		: [] -> []
		| [h] -> [h]
		| [h, *t] -> [h, *.prefix(t, s)]
		;
	
	prefix(p)
		: [] -> []
		| [h, *t] -> [p, h, *.prefix(t, p)]
		;
	
	string
		: _ -> H(["\"", _, "\""], 0)
		;

header {
def ir2box(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = Ir2Box(term.getFactory())
	box = boxer.convert(term)
	return box
}
