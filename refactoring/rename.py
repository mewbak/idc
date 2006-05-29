"""Rename symbols globally."""


import refactoring
import path
import transf


class Rename(refactoring.Refactoring):

	def name(self):
		return "Rename"
	
	def get_original_name(self, term, selection):
		start, end = selection
		if start != end:
			return False

		selected_term = path.fetch(term, start)
		args = []
		kargs = {}
		if selected_term.rmatch("Sym(name)", args, kargs):
			return kargs['name']
		else:
			return None

	def applicable(self, term, selection):
		return self.get_original_name(term, selection) is not None

	def input(self, term, selection, inputter):
		factory = term.factory
		orig = self.get_original_name(term, selection)
		new = factory.makeStr(inputter.inputStr(
			title = "Rename", 
			text = "New name?"
		))
		args = factory.make("[orig,new]", orig=orig, new=new)
		return args

	def apply(self, term, args):
		factory = term.factory
		src, dst = args
		import transf
		txn = transf.Rule("Sym(src)", "Sym(dst)", src = src, dst = dst)
		txn = transf.InnerMost(txn)
		return txn(term)


class TestCase(refactoring.TestCase):

	cls = Rename
		
	applyTestCases = [
		('Sym("a")', '["a", "b"]', 'Sym("b")'),
		('Sym("c")', '["a", "b"]', 'Sym("c")'),
		('[Sym("a"),Sym("c")]', '["a", "b"]', '[Sym("b"),Sym("c")]'),
		('C(Sym("a"),Sym("c"))', '["a", "b"]', 'C(Sym("b"),Sym("c"))'),
	]