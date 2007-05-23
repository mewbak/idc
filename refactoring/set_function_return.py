"""Set Function Return"""


from transf import parse
import ir.traverse
import ir.path


parse.Transfs('''

applicable =
	ir.path.projectSelection ; ?Function(Void, _, _, _)

input =
	with name, ret in
		ir.path.projectSelection ; ?Function(_, name, _, _) ;
		input.Str(!"Set Function Return", !"Return Symbol?") ; ?ret ;
		![name, ret]
	end

apply =
	with name, type, ret in
		Where(!args; ?[name, ret]) ;
		Where(!Int(32,Signed); ?type) ;
		~Module(<
			One(
				~Function(!type, ?name, _, <
					AllTD(~Ret(!type, !Sym(ret)))
				>)
			)
		>) ;
		ir.traverse.AllStmtsBU(Try(
			?Assign(Void, NoExpr, Call(Sym(?name), _)) ;
			~Assign(!type, !Sym(ret), _)
		))
	end


testApply =
	!Module([
		Function(Void,"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Void,NoExpr)
		]),
	]) ;
	with selection = ![0,0], args = !["main","eax"] in apply end ;
	?Module([
		Function(Int(32,Signed),"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Int(32,Signed),Sym("eax"))
		]),
	])

''')
