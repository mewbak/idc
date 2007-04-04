"""Extract Function"""


from transf import lib
import ir.path


lib.parse.Transfs('''

goto =
	ir.path.inSelection ;
	?GoTo(Sym(label))

applicable =
	~Module(<lists.Fetch(ir.path.isSelected ; ?Label(_) )>)

input =
	ir.path.projectSelection ;
	( Label(label) -> [label] )

apply =
	with label in
		Where(!args; ?[label]) ;
		~Module(<AtSuffix(
			with rest in
				~[Label(?label), *<AtSuffix(
					~[Ret(_,_), *<?rest ; ![]>]
				)>] ;
				![Function(Void, label, [], <project.tail>), *rest]
			end
		)>)
	end


testApply =
	!Module([
		Asm("pre",[]),
		Label("main"),
		Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
		Ret(Int(32,Signed),Sym("eax")),
		Asm("post",[]),
	]) ;
	with selection = ![0,1], args = !["main"] in apply end ;
	?Module([
		Asm("pre",[]),
		Function(Void,"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Int(32,Signed),Sym("eax"))
		]),
		Asm("post",[]),
	])

''')
