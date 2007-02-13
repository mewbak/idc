"""Rename Symbol"""


from transf import lib
import ir.path

lib.parse.Transfs(r'''

applicable = ir.path.projectSelection ; ?Sym(_)

input =
	with src, dst in
		ir.path.projectSelection ; ?Sym(src) ;
		lib.input.Str(!"Set Function Return", !"Return Symbol?") ; ?dst ;
		![src, dst]
	end

apply =
	with src, dst in
		Where(!args; ?[src, dst]) ;
		AllTD(
			~Sym(<?src; !dst>) +
			~Arg(_, <?src; !dst>)
		)
	end
''')

applyTestCases = [
	('Sym("a")', '[[], "a", "b"]', 'Sym("b")'),
	('Sym("c")', '[[], "a", "b"]', 'Sym("c")'),
	('[Sym("a"),Sym("c")]', '[[], "a", "b"]', '[Sym("b"),Sym("c")]'),
	('C(Sym("a"),Sym("c"))', '[[], "a", "b"]', 'C(Sym("b"),Sym("c"))'),
]
