"""Perform global simplifications."""


import refactoring
import transf


class Rename(refactoring.Refactoring):

	def name(self):
		return "Simplify"
	
	def applicable(self, term, selection):
		return True

	def input(self, term, selection, inputter):
		return term.factory.makeNil()

	def apply(self, term, args):
		factory = term.factory
		rules = [
			('Assign(type,dst,Cond(cond,src,dst)))',
				'If(cond, Assign(type,dst,src),NoOp)'),
			('Assign(type,dst,Cond(cond,src,dst)))',
				'If(Not(cond), Assign(type,dst,src),NoOp)'),
		
			('Assign(_,Sym("pc"),expr)', 
				'Branch(Addr(expr))'),
			
			('Cond(cond,Lit(Int(_,_),1),Lit(Int(_,_),0))',
				'cond'),
			('Cond(cond,Lit(Int(_,_),0),Lit(Int(_,_),1))',
				'Not(cond)'),

			('Ref(Addr(expr))',
				'expr'),
			('Addr(Ref(expr))',
				'expr'),
		]
		txn = transf.rewrite.RuleSet(rules)
		#txn = transf.Repeat(txn)
		txn = transf.traverse.InnerMost(txn)
		return txn(term)


class TestCase(refactoring.TestCase):

	cls = Rename
		
	applyTestCases = [
			('Assign(Blob(32),Sym("pc"),Ref(Sym("label")))', '[]',
				'Branch(Sym("label"))'),	
			('Assign(Blob(32),Sym("pc"),Cond(Sym("flag"),Ref(Sym("label")),Sym("pc")))', '[]',
				'If(Sym("flag"),Branch(Sym("label")),NoOp)'),		
	]
