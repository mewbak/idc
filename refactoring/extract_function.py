"""Extract a function body."""


import refactoring
import path
import transf
from transf import *
from ir.transfs import *


class ExtractFunction(refactoring.Refactoring):

	def name(self):
		return "Extract Function"
	
	def get_original_name(self, term, selection):
		start, end = selection
		if start != end:
			return False

		selected_term = path.fetch(term, start)
		mo = selected_term.rmatch("Label(name)")
		if mo:
			return mo.kargs['name']
		else:
			return None
		
	def applicable(self, term, selection):
		return self.get_original_name(term, selection) is not None

	def input(self, term, selection, inputter):
		factory = term.factory
		label = self.get_original_name(term, selection)
		args = factory.make("[label]", label = label)
		return args

	def apply(self, term, args):
		factory = term.factory
		name, = args
		txn = transf.rewrite.Rule(
			"[Label(name),*rest]",
			"[FuncDef(Void,name,[],Block(rest))]",
		)
		txn = transf.traverse.TraverseAppl(
			'Module',
			[ExtractBlock(txn,name)]
		)
		# TODO: Handle seperate blocks
		return txn(term)


class TestCase(refactoring.TestCase):

	cls = ExtractFunction
		
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
				FuncDef(Void,"main",[],
					Block([
						Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
						Ret(Int(32,Signed),Sym("eax"))
					])
				)
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
				FuncDef(Void,"main",[],
					Block([
						Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
						Ret(Int(32,Signed),Sym("eax"))
					])
				),
				Asm("post",[]),
			])
			'''
		),	]
	
	