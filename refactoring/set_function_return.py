"""Set Function Return"""


from transf import lib
import ir.traverse
import ir.path


lib.parse.Transfs('''

applicable =
	ir.path.projectSelection ; ?Function(Void, _, _, _)

input =
	with name, ret in
		ir.path.projectSelection ; ?Function(_, name, _, _) ;
		lib.input.Str(!"Set Function Return", !"Return Symbol?") ; ?ret ;
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

''')


applyTestCases = [
	(
		'''
		Module([
			Function(Void,"main",[],[
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Void,NoExpr)
			]),
		])
		''',
		'[[0,0],"main","eax"]',
		'''
		Module([
			Function(Int(32,Signed),"main",[],[
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Int(32,Signed),Sym("eax"))
			]),
		])
		'''
	)
]


