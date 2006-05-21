#!/usr/bin/env python


import unittest

import aterm

from transformations import *


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.Factory()

	annotatorTestCases = [
		('1', '1{Path,[]}'),
		('[1,2]', '[1{Path,[0]},2{Path,[1]}]{Path,[]}'),
		('C(1,2)', 'C(1{Path,[0]},2{Path,[1]}){Path,[]}'),
	]
	
	def checkTransf(self, transformation, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			try:
				result = transformation(term)
			except Failure:
				result = self.factory.parse("FAILURE")
			
			self.failUnlessEqual(result, expectedResult)

	identTestCases = [
		('1', '1'),
		('0.1', '0.1'),
		('"s"', '"s"'),
		('[1,2]', '[1,2]'),
		('C(1,2)', 'C(1,2)'),
		('_', '_'),
		('x', 'x'),
	]

	def testIdent(self):
		self.checkTransf(Ident(), self.identTestCases)

	failTestCases = [
		('1', 'FAILURE'),
		('0.1', 'FAILURE'),
		('"s"', 'FAILURE'),
		('[1,2]', 'FAILURE]'),
		('C(1,2)', 'FAILURE'),
		('_', 'FAILURE'),
		('x', 'FAILURE'),
	]	
	
	def testFail(self):
		self.checkTransf(Fail(), self.failTestCases)
	
	def testNot(self):
		self.checkTransf(Not(Ident()), self.failTestCases)
		self.checkTransf(Not(Fail()), self.identTestCases)
	
	def testTry(self):
		self.checkTransf(Try(Ident()), self.identTestCases)
		self.checkTransf(Try(Fail()), self.identTestCases)

	def testOr(self):
		self.checkTransf(Or(Ident(), Ident()), self.identTestCases)
		self.checkTransf(Or(Ident(), Fail()), self.identTestCases)
		self.checkTransf(Or(Fail(), Ident()), self.identTestCases)
		self.checkTransf(Or(Fail(), Fail()), self.failTestCases)
		
	def testAnd(self):
		self.checkTransf(And(Ident(), Ident()), self.identTestCases)
		self.checkTransf(And(Ident(), Fail()), self.failTestCases)
		self.checkTransf(And(Fail(), Ident()), self.failTestCases)
		self.checkTransf(And(Fail(), Fail()), self.failTestCases)

	# FIXME: write the remaining test cases


if __name__ == '__main__':
	unittest.main()
