"""Classes for modelling and applying refactories."""


import os

import aterm.factory
import unittest


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
			if refactoring.applicable(term, selection):
				yield refactoring
		raise StopIteration

	def from_name(self, name):
		"""Return the refactoring with the specified name."""
		return self.refactorings[name]




class TestCase(unittest.TestCase):
	'''Base class for refactoring unittests.'''
	
	cls = Refactoring
	
	def setUp(self):
		self.factory = aterm.factory.factory
		self.refactoring = self.cls()
	
	applyTestCases = []
	
	def testApply(self):			
		for termStr, argsStr, expectedResultStr in self.applyTestCases:
			term = self.factory.parse(termStr)
			args = self.factory.parse(argsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = self.refactoring.apply(term, args)
			
			self.failUnlessEqual(result, expectedResult)
			

def main(cls):
	import aterm.factory
	import sys
	import ir.pprint
	from lang import box
	factory = aterm.factory.factory
	if len(sys.argv) < 1:
		sys.exit(1)
	term = factory.readFromTextFile(file(sys.argv[1], 'rt'))
	args = factory.parse('[' + ','.join(sys.argv[2:]) + ']')

	sys.stdout.write('*** BEFORE ***\n')
	box.write(
		ir.pprint.module(term), 
		box.AnsiTextFormatter(sys.stdout)
	)

	refactoring = cls()
	term = refactoring.apply(term, args)
	
	sys.stdout.write('*** AFTER ***\n')
	box.write(
		ir.pprint.module(term), 
		box.AnsiTextFormatter(sys.stdout)
	)
