"""Classes for modelling and applying refactories."""


import os


class BaseException(Exception):
	"""Base class for refactoring-related exceptions."""

	pass
	

class Refactoring:
	"""Base class for concrete refactorings."""

	def __init__(self):
		pass
	
	def name(self):
		"""Rerturn a description of this refactoring. Used for persistency,
		roolback, etc."""
		raise NotImplementedError

	def applicable(self, term, selection):
		"""Verifies the pre-conditions for applying this refactory are met."""
		raise NotImplementedError

	def input(self, term, selection, inputter):
		"""Ask user input. It should return a list of arguments."""
		raise NotImplementedError
	
	def apply(self, term, args):
		"""Apply the refactory."""
		raise NotImplementedError


class Factory:
	"""Factory for refactories."""
	
	def __init__(self):
		"""Initialize the factory, populating with the list of known 
		refactorings.
		"""
		self.refactorings = {}
		for path in __path__:
			for name in os.listdir(path):
				name, ext = os.path.splitext(name)
				if name != '__init__' and ext == '.py':
					module = __import__(__name__ + '.' + name)
					module = getattr(module, name)
					for nam, cls in module.__dict__.iteritems():
						try:
							print issubclass(cls, Refactoring)
							if issubclass(cls, Refactoring):
								refactoring = cls()
								self.refactorings[refactoring.name()] = refactoring
						except TypeError:
							pass
							

	def applicables(self, term, selection):
		"""Enumerate the applicable refactorings to the given term and 
		selection context.
		"""
		for refactoring in self.refactorings.itervalues():
			print refactoring.name() + "..."
			if refactoring.applicable(term, selection):
				yield refactoring
		raise StopIteration

	def from_name(self, name):
		"""Return the refactoring with the specified name."""
		return self.refactorings[name]

