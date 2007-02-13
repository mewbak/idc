"""Classes for modelling and applying refactories."""


import os
import unittest

import aterm.factory
import transf.exception


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

	def input(self, term, selection):
		"""Ask user input. It should return a list of arguments."""
		raise NotImplementedError

	def apply(self, term, args):
		"""Apply the refactory."""
		raise NotImplementedError


class ModuleRefactoring(Refactoring):

	def __init__(self, module):
		self.module = module
		try:
			self._applicable = self.module.applicable
			self._input = self.module.input
			self._apply = self.module.apply
		except AttributeError:
			raise ValueError("not a refactoring module %s", module.__name__)

	def name(self):
		return self.module.__doc__

	def applicable(self, term, selection):
		start, end = selection
		selection = aterm.path.ancestor(start, end)
		try:
			self._applicable(term, selection=selection)
		except transf.exception.Failure:
			return False
		else:
			return True

	def input(self, term, selection):
		factory = term.factory
		start, end = selection
		selection = aterm.path.ancestor(start, end)
		args = self._input(term, selection=selection)
		args = factory.make("[_,*]", selection, args)
		return args

	def apply(self, term, args):
		selection = args.head
		args = args.tail
		try:
			return self._apply(term, selection=selection, args=args)
		except transf.exception.Failure, ex:
			raise
			return term

	def testApply(self):
		factory = aterm.factory.factory
		for termStr, argsStr, expectedResultStr in self.module.applyTestCases:
			term = factory.parse(termStr)
			args = factory.parse(argsStr)
			expectedResult = factory.parse(expectedResultStr)

			term = aterm.path.annotate(term)
			result = self.apply(term, args)

			assert result == expectedResult

	def getTests(self):
		return unittest.FunctionTestCase(self.testApply, description=self.module.__name__)


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
					for nam, obj in module.__dict__.iteritems():
						try:
							if isinstance(obj, Refactoring):
								refactoring = obj
								self.refactorings[refactoring.name()] = refactoring
							if issubclass(obj, Refactoring):
								refactoring = obj()
								self.refactorings[refactoring.name()] = refactoring
						except TypeError:
							pass
					try:
						refactoring = ModuleRefactoring(module)
						self.refactorings[refactoring.name()] = refactoring
					except ValueError:
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

	refactoring = None

	def setUp(self):
		self.factory = aterm.factory.factory

	applyTestCases = []

	def testApply(self):
		for termStr, argsStr, expectedResultStr in self.applyTestCases:
			term = self.factory.parse(termStr)
			args = self.factory.parse(argsStr)
			expectedResult = self.factory.parse(expectedResultStr)

			result = self.refactoring.apply(term, args)

			self.failUnlessEqual(result, expectedResult)


def main(obj):
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

	if isinstance(obj, Refactoring):
		refactoring = obj
	elif issubclass(obj, Refactoring):
		refactoring = obj()
	term = refactoring.apply(term, args)

	sys.stdout.write('*** AFTER ***\n')
	box.write(
		ir.pprint.module(term),
		box.AnsiTextFormatter(sys.stdout)
	)
