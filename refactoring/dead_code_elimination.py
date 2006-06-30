"""Dead code elimination."""


import refactoring
import transf
from transf import path
import ir.dce


class DeadCodeElimination(refactoring.Refactoring):

	def name(self):
		return "Dead Code Elimination"
	
	def applicable(self, term, selection):
		return True

	def input(self, term, selection):
		factory = term.factory
		args = factory.make("[]")
		return args

	def apply(self, term, args):
		factory = term.factory
		txn = ir.dce.dce		
		return txn(term)


class TestCase(refactoring.TestCase):

	cls = DeadCodeElimination


if __name__ == '__main__':
	refactoring.main(DeadCodeElimination)