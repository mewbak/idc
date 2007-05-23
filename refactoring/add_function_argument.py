"""Add Function Argument"""


from transf import parse
import ir.traverse
import ir.path


parse.Transfs('''

applicable =
	ir.path.projectSelection ; ?Function(_, _, _, _)

input =
	with name, arg in
		ir.path.projectSelection ; ?Function(_, ?name, _, _) ;
		input.Str(!"Add Function Argument", !"Argument Symbol?") ; ?arg ;
		![name, arg]
	end

apply =
	with name, type, arg in
		Where(!args; ?[name, arg]) ;
		Where(!Int(32,Signed); ?type) ;
		~Module(<
			One(
				~Function(_, ?name, <Concat(id,![Arg(type,arg)])>, _)
			)
		>) ;
		BottomUp(Try(
			~Call(Sym(?name), <Concat(id,![Sym(arg)])>)
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
		Function(Void,"main",[Arg(Int(32,Signed),"eax")],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Void,NoExpr)
		]),
	])

''')