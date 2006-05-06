#!/usr/bin/env python


import unittest

import aterm
import path


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.Factory()
		self.annotator = path.Annotator(self.factory)

	def parseArgs(self, args):
		return [self.factory.parse(value) for value in args]
	
	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = self.factory.parse(value)
		return res
	
	annotatorTestCases = [
		('1', '1{Path,[]}'),
		('[1,2]', '[1{Path,[Index(0)]},2{Path,[Index(1)]}]{Path,[]}'),
		('C(1,2)', 'C(1{Path,[Arg(0)]},2{Path,[Arg(1)]}){Path,[]}'),
	]
	
	def testAnnotator(self):
		for termStr, expectedResultStr in self.annotatorTestCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = self.annotator.anno(term)
			
			self.failUnlessEqual(result, expectedResult)
			
			self.failUnless(result.isEquivalent(term))
			self.failUnless(term.isEquivalent(result))


if __name__ == '__main__':
	unittest.main()