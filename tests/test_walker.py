#!/usr/bin/env python


import unittest

import aterm.factory
import walker


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.factory.Factory()
		self.walker = walker.Walker(self.factory)
		self.target = self.factory.parse("Test")

	def testFail(self):	
		try:
			self.walker._fail(self.target)
		except walker.Failure:
			pass
		else:
			self.fail()
	
	def testAssertFail(self):	
		try:
			self.walker._assertFail(self.target)
		except AssertionError:
			pass
		else:
			self.fail()
	
	mapTestCases = [
		('[]', lambda x: x.factory.makeInt(x.getValue()*2), [], {}, '[]'),
		('[0,1,2,3]', lambda x: x.factory.makeInt(x.getValue()*2), [], {}, '[0,2,4,6]'),
		('[]', lambda x, y: x.factory.makeInt(x.getValue()*y), [2], {}, '[]'),
		('[0,1,2,3]', lambda x, y: x.factory.makeInt(x.getValue()*y), [2], {}, '[0,2,4,6]'),
	]
	
	def testMap(self):
		for targetStr, func, args, kargs, expectedResultStr in self.mapTestCases:
			target = self.factory.parse(targetStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = self.walker._map(target, func, *args, **kargs)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s => %r (!= %s)' % (targetStr, result, expectedResult))
	
	catManyTestCases = [
		('[]', '[]'),
		('[[1,2,3,4,5,6]]', '[1,2,3,4,5,6]'),
		('[[1,2,3],[4,5,6]]', '[1,2,3,4,5,6]'),
		('[[1,2],[3,4],[5,6]]', '[1,2,3,4,5,6]'),
		('[[1,2,3],[]]', '[1,2,3]'),
		('[[],[1,2,3]]', '[1,2,3]'),
	]
	
	def testCatMany(self):
		for targetStr, expectedResultStr in self.catManyTestCases:
			target = self.factory.parse(targetStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = self.walker._catMany(target)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s => %r (!= %s)' % (targetStr, result, expectedResult))
			

if __name__ == '__main__':
	unittest.main()
