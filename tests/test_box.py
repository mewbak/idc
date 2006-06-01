#!/usr/bin/env python


import unittest

import aterm.factory
import box


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.factory.Factory()

	def parseArgs(self, args):
		return [self.factory.parse(value) for value in args]
	
	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = self.factory.parse(value)
		return res
	
	box2TextTestCases = [
		('"a"', 'a\n'),
		('H(["a","b"])', 'ab\n'),
		('V(["a","b"])', 'a\nb\n'),
		('V(["a",I("b"),"c"])', 'a\n\tb\nc\n'),
	]
	
	def testBox2Text(self):
		for inputStr, expectedOutput in self.box2TextTestCases:
			input = self.factory.parse(inputStr)
		
			output = box.box2text(input)
			
			self.failUnlessEqual(output, expectedOutput)

	term2BoxTestCases = [
	]
	
	def _testTerm2Box(self):
		for inputStr, expectedOutput in self.term2BoxTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = box.term2box(input)
			output = box.box2text(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
