"""Extract a function body."""


import refactoring
from refactoring._common import CommonRefactoring

import transf as lib
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
				![Function(Void, label, [], <project.tail>), *rest] ;
				debug.Dump()
			end
		)>)
	end
''')

extractFunction = CommonRefactoring("Extract Function", applicable, input, apply)


class TestCase(refactoring.TestCase):

	refactoring = extractFunction
		
	applyTestCases = [
		(
			'''
			Module([
				Label("main"),
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Int(32,Signed),Sym("eax"))
			])
			''',
			'["main"]',
			'''
			Module([
				Function(Void,"main",[],[
					Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
					Ret(Int(32,Signed),Sym("eax"))
				])
			])
			'''
		),
		(
			'''
			Module([
				Asm("pre",[]),
				Label("main"),
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Int(32,Signed),Sym("eax")),
				Asm("post",[]),
			])
			''',
			'["main"]',
			'''
			Module([
				Asm("pre",[]),
				Function(Void,"main",[],[
					Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
					Ret(Int(32,Signed),Sym("eax"))
				]),
				Asm("post",[]),
			])
			'''
		),	]
	

if __name__ == '__main__':
	refactoring.main(extractFunction)


