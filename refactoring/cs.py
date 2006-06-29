"""Consolidate."""


import refactoring
import paths
import transf as lib
from ir import cs, match
from ir.path import *

lib.parse.Transfs('''

applicable = matchSelectionTo(?GoTo(Sym(_)))


apply = cs.do


''')




class Consolidate(refactoring.Refactoring):

	def name(self):
		return __doc__
	
	def applicable(self, term, selection):
		start, end = selection
		selection = paths.ancestor(start, end)
		print selection
		try:
			applicable(term, selection=selection)
		except lib.exception.Failure:
			return False
		else:
			return True

	def input(self, term, selection, inputter):
		factory = term.factory
		start, end = selection
		selection = paths.ancestor(start, end)
		args = factory.make("[_]", selection)
		return args

	def apply(self, term, args):
		selection, = args
		try:
			return apply(term, selection=selection)
		except lib.exception.Failure:
			return False


if __name__ == '__main__':
	refactoring.main(Consolidate)