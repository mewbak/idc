"""Consolidate."""


import refactoring
import transf
from transf import path
import ir.cs


class Consolidate(refactoring.Refactoring):

	def name(self):
		return "Consolidate"
	
	def applicable(self, term, selection):
		return True

	def input(self, term, selection, inputter):
		factory = term.factory
		args = factory.make("[]")
		return args

	def apply(self, term, args):
		factory = term.factory
		txn = ir.cs.do
		return txn(term)


if __name__ == '__main__':
	refactoring.main(Consolidate)