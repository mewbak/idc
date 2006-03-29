#!/usr/bin/env python


import unittest

import aterm
import box
import ir


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
	
	checkerTestCases = [
		("module", "Module([])", True),
		("module", "XXX", False),
	]
	
	def testChecker(self):
		checker = ir.Checker(self.factory)

		for methodName, inputStr, expectedOutput in self.checkerTestCases:
			input = self.factory.parse(inputStr)
		
			try:
				getattr(checker, methodName)(input)
				output = True
			except ir.Failure:
				output = False
			
			self.failUnlessEqual(
					output, expectedOutput, 
					msg = '%s(%s) = %r (%r expected)' % (methodName, inputStr, output, expectedOutput)
			)

	prettyPrinterTestCases = [
		('Label("a")', 'a:'),
		('Assembly("ret",[])', 'asm("ret")'),
		('Assembly("mov",[Register("ax"), Constant(1234)])', 'asm("mov", ax, 1234)'),
	]
	
	def testPrettyPrinter(self):
		for inputStr, expectedOutput in self.prettyPrinterTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = ir.prettyPrint(input)
			output = box.box2text(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
