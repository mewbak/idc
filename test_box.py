#!/usr/bin/env python


import unittest

import aterm
import box


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.Factory()

	def parseArgs(self, args):
		return [self.factory.parse(value) for value in args]
	
	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = self.factory.parse(value)
		return res
	
	box2TextTestCases = [
		('"a"', 'a'),
		('H(["a","b"],0)', 'ab'),
		('H(["a","b"],1)', 'a b'),
		('V(["a","b"],1)', 'a\nb\n'),
		('V(["a","b"],2)', 'a\n\nb\n\n'),
		('V(["a",I("b",1),"c"],1)', 'a\n\tb\nc\n'),
	]
	
	def testBox2Text(self):
		for inputStr, expectedOutput in self.box2TextTestCases:
			input = self.factory.parse(inputStr)
		
			output = box.box2text(input)
			
			self.failUnlessEqual(output, expectedOutput)

	term2BoxTestCases = [
	]
	
	def testTerm2Box(self):
		for inputStr, expectedOutput in self.term2BoxTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = box.term2box(input)
			output = box.box2text(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
