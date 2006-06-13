"""Set function return."""


import refactoring
import transf
import path
import ir.transfs


class SetFunctionReturn(refactoring.Refactoring):

	def name(self):
		return "Set Function Return"
	
	def get_original_name(self, term, selection):
		start, end = selection
		if start != end:
			return None

		selected_term = path.fetch(term, start)
		mo = selected_term.rmatch("FuncDef(_,name,*)")
		if mo:
			print mo.kargs
			return mo.kargs['name']
		else:
			return None

	def applicable(self, term, selection):
		return self.get_original_name(term, selection) is not None

	def input(self, term, selection, inputter):
		factory = term.factory
		name = self.get_original_name(term, selection)
		print name
		ret = factory.makeStr(inputter.inputStr(
			title = self.name(), 
			text = "Return symbol?"
		))
		args = factory.make("[name,ret]", name=name, ret=ret)
		return args

	def apply(self, term, args):
		factory = term.factory
		print args
		name, ret = args

		name = transf.match.Term(name)
		typ = transf.build.Term('Int(32,Signed)')
		ret = transf.build.Term(ret)
		
		txn = transf.parse.Transf('''
			alltd(
				~FuncDef(<typ>, <name>, _, 
					<alltd(~Ret(<typ>,<!Sym(<ret>)>))>
				)
			)
		''')
		return txn(term)


if __name__ == '__main__':
	refactoring.main(SetFunctionReturn)