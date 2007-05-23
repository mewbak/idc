"""Rename Symbol"""


from transf import parse
import ir.path


parse.Transfs(r'''

applicable =
	ir.path.projectSelection ;
	?Sym(_)

input =
	with src, dst in
		ir.path.projectSelection ; ?Sym(src) ;
		input.Str(!"Set Function Return", !"Return Symbol?") ; ?dst ;
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


doTestApply =
	with args = !["a", "b"] in apply end

testNoRename =
	!Sym("c") ;
	doTestApply ;
	?Sym("c")

testRename =
	!Sym("a") ;
	doTestApply ;
	?Sym("b")

testRenameInList =
	![Sym("a"),Sym("c")] ;
	doTestApply ;
	?[Sym("b"),Sym("c")]

testRenameInAppl =
	!C(Sym("a"),Sym("c")) ;
	doTestApply ;
	?C(Sym("b"),Sym("c"))

''')
