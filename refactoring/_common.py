'''Common transformation-based refactoring.'''


import refactoring
import transf
import paths


class CommonRefactoring(refactoring.Refactoring):

	def __init__(self, name, applicable, input, apply):
		self._name = name
		self._applicable = applicable
		self._input = input
		self._apply = apply
		
	def name(self):
		return self._name
	
	def applicable(self, term, selection):
		start, end = selection
		selection = paths.ancestor(start, end)
		try:
			self._applicable(term, selection=selection)
		except transf.exception.Failure:
			return False
		else:
			return True

	def input(self, term, selection):
		factory = term.factory
		start, end = selection
		selection = paths.ancestor(start, end)
		args = self._input(term, selection=selection)
		args = factory.make("[_,*]", selection, args)
		return args

	def apply(self, term, args):
		selection = args.head
		args = args.tail
		try:
			return self._apply(term, selection=selection, args=args)
		except transf.exception.Failure:
			return term

		
		