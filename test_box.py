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
		('S("a")', 'a'),
		('H([S("a"),S("b")],0)', 'ab'),
		('H([S("a"),S("b")],1)', 'a b'),
		('V([S("a"),S("b")],1,0)', 'a\nb\n'),
		('V([S("a"),S("b")],1,1)', '\ta\n\tb\n'),
	]
	
	def testBox2Text(self):
		for inputStr, expectedOutput in self.box2TextTestCases:
			input = self.factory.parse(inputStr)
		
			output = box.box2text(input)
			
			self.failUnlessEqual(output, expectedOutput)

	c2BoxTestCases = [
		('Label("a")', 'a:'),
		('Assembly("a",[])', 'asm("a")'),
	]
	
	def testC2Box(self):
		for inputStr, expectedOutput in self.c2BoxTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = box.c2box(input)
			print boxes
			output = box.box2text(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
