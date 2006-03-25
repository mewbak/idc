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
	
	ir2BoxTestCases = [
		('Label("a")', 'a:'),
		('Assembly("ret",[])', 'asm("ret")'),
		('Assembly("mov",[Register("ax"), Constant(1234)])', 'asm("mov", ax, 1234)'),
	]
	
	def testIr2Box(self):
		for inputStr, expectedOutput in self.ir2BoxTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = ir.ir2box(input)
			output = box.box2text(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
