"""Rename symbols globally."""


import refactoring
import path


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
		if term.factory.match("Sym(name)", selected_term, args, kargs):
			return kargs['name']
		else:
			return None

	def applicable(self, term, selection):
		return self.get_original_name(term, selection) is not None

	def input(self, term, selection, inputter):
		factory = term.factory
		orig = self.get_original_name(term, selection)
		new = factory.makeStr(inputter.inputStr(title = "Rename", text = "New name?"))
		args = factory.make("[orig,new]", orig = orig, new = new)
		return args

	def apply(self, term, args):
		factory = term.factory
		src, dst = args
		import transf
		txn = transf.Rule(
			factory.make("Sym(_)", src),
			factory.make("Sym(_)", dst),
		)
		txn = transf.InnerMost(txn)
		return txn(term)



import unittest


class TestCase(unittest.TestCase):
	
	def setUp(self):
		import aterm
		self.factory = aterm.Factory()
	
	renameTestCases = [
		('Sym("a")', '["a", "b"]', 'Sym("b")'),
		('Sym("c")', '["a", "b"]', 'Sym("c")'),
		('[Sym("a"),Sym("c")]', '["a", "b"]', '[Sym("b"),Sym("c")]'),
		('C(Sym("a"),Sym("c"))', '["a", "b"]', 'C(Sym("b"),Sym("c"))'),
	]
	
	def testRename(self):
		for termStr, argsStr, expectedResultStr in self.renameTestCases:
			term = self.factory.parse(termStr)
			args = self.factory.parse(argsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			refactoring = Rename()
			
			result = refactoring.apply(term, args)
			
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
