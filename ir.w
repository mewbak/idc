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
def ir2box(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = Ir2Box(term.getFactory())
	box = boxer.convert(term)
	return box
}
