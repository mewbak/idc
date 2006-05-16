"""Classes for modelling and applying refactories."""


class BaseException(Exception):
	"""Base class for refactoring-related exceptions."""

	pass


class Factory:
	"""Factory for refactories."""
	
	def make(self, description):
		"""Instantiate a refactory from the specified description."""
		
		# TODO: do some argument sanity checking here
		
		name = descriptions.getName()
		args = descriptions.getArgs()

		name = name.getValue()
		args = list(args)

		module = __import__('refactorings.' + name.tolower())

		refactoring = module.Refactoring(*args)
		return refactoring
	

class Refactoring:
	"""Base class for concrete refactorings."""

	def __init__(self):
		pass

	def pre_conditions(self, term):
		"""Verifies the pre-conditions for applying this refactory are met."""
		raise NotImplementedError

	def apply(self, term):
		"""Apply the refactory."""
		raise NotImplementedError
		
	def describe(self):
		"""Rerturn a description of this refactoring. Used for persistency,
		roolback, etc."""
		raise NotImplementedError

	def can_commute(self, other):
		"""Whether this refactoring can commute with another _consecutive_ refactoring."""
		# FIXME: Is this really necessary
		raise NotImplementedError


