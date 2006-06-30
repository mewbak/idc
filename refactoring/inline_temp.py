"""Inline Temp."""


import refactoring
import transf
from transf import path
import ir.prop


class InlineTemp(refactoring.Refactoring):

	def name(self):
		return "Inline Temp"
	
	def applicable(self, term, selection):
		return True

	def input(self, term, selection):
		factory = term.factory
		args = factory.make("[]")
		return args

	def apply(self, term, args):
		factory = term.factory
		txn = ir.prop.prop
		return txn(term)


if __name__ == '__main__':
	refactoring.main(InlineTemp)