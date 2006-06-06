#!/usr/bin/env python


import unittest

import aterm.factory
import transf
import path


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
	
	annotatorTestCases = [
		('1', '1{Path([])}'),
		('[1,2]', '[1{Path([0])},2{Path([1])}]{Path([])}'),
		('C(1,2)', 'C(1{Path([0])},2{Path([1])}){Path([])}'),
		('[[[]]]', '[[[]{Path([0,0])}]{Path([0])}]{Path([])}'),
		('C(C(C))', 'C(C(C{Path([0,0])}){Path([0])}){Path([])}'),
		('[[1],[2]]', '[[1{Path([0,0])}]{Path([0])},[2{Path([0,1])}]{Path([1])}]{Path([])}'),
		('C(C(1),C(2))', 'C(C(1{Path([0,0])}){Path([0])},C(2{Path([0,1])}){Path([1])}){Path([])}'),
	]
	
	def testAnnotate(self):
		for termStr, expectedResultStr in self.annotatorTestCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.annotate(term)
			
			self.failUnlessEqual(result, expectedResult)
			
			self.failUnless(result.isEquivalent(term))
			self.failUnless(term.isEquivalent(result))

	def checkTransformation(self, metaTransf, testCases):
		for termStr, pathStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = metaTransf(_path)(term)
			
			self.failUnlessEqual(result, expectedResult)
			
	fetchTestCases = [
		('1', '[]', '1'),
		('[1,2]', '[]', '[1,2]'),
		('[1,2]', '[0]', '1'),
		('[1,2]', '[1]', '2'),
		('C(1,2)', '[]', 'C(1,2)'),
		('C(1,2)', '[0]', '1'),
		('C(1,2)', '[1]', '2'),
		('A([B,C],[D,E])', '[0,0]', 'B'),
		('A([B,C],[D,E])', '[1,0]', 'C'),
		('A([B,C],[D,E])', '[0,1]', 'D'),
		('A([B,C],[D,E])', '[1,1]', 'E'),
	]

	def testFetch(self):
		self.checkTransformation(
			path.PathFetch, 
			self.fetchTestCases
		)
	
	pathTestCases = [
		('1', '[]', 'X(1)'),
		('[1,2]', '[]', 'X([1,2])'),
		('[1,2]', '[0]', '[X(1),2]'),
		('[1,2]', '[1]', '[1,X(2)]'),
		('C(1,2)', '[]', 'X(C(1,2))'),
		('C(1,2)', '[0]', 'C(X(1),2)'),
		('C(1,2)', '[1]', 'C(1,X(2))'),
		('A([B,C],[D,E])', '[0,1]', 'A([B,C],[X(D),E])'),
		('A([B,C],[D,E])', '[1,0]', 'A([B,X(C)],[D,E])'),
	]	
	
	def testPath(self):
		self.checkTransformation(
			lambda _path: path.Path(transf.rewrite.Rule('x', 'X(x)'), _path),
			self.pathTestCases
		)

	splitTestCases = [
		('[0,1,2,3]', 0, '[]', '[0,1,2,3]'),
		('[0,1,2,3]', 1, '[0,]', '[1,2,3]'),
		('[0,1,2,3]', 2, '[0,1,]', '[2,3]'),
		('[0,1,2,3]', 3, '[0,1,2,]', '[3]'),
		('[0,1,2,3]', 4, '[0,1,2,3]', '[]'),
	]
	
	def testSplit(self):
		for inputStr, index, expectedHeadStr, expectedTailStr in self.splitTestCases:
			input = self.factory.parse(inputStr)
			expectedHead = self.factory.parse(expectedHeadStr)
			expectedTail = self.factory.parse(expectedTailStr)
			
			head, tail = path.split(input, index)
			
			self.failUnlessEqual(head, expectedHead)
			self.failUnlessEqual(tail, expectedTail)

	rangeTestCases = [
		('[0,1,2]', 0, 0, '[0,1,2]'),
		('[0,1,2]', 0, 1, '[X(0),1,2]'),
		('[0,1,2]', 0, 2, '[X(0),X(1),2]'),
		('[0,1,2]', 0, 3, '[X(0),X(1),X(2)]'),
		('[0,1,2]', 1, 1, '[0,1,2]'),
		('[0,1,2]', 1, 2, '[0,X(1),2]'),
		('[0,1,2]', 1, 3, '[0,X(1),X(2)]'),
		('[0,1,2]', 2, 2, '[0,1,2]'),
		('[0,1,2]', 2, 3, '[0,1,X(2)]'),
		('[0,1,2]', 3, 3, '[0,1,2]'),
	]	
	
	def testRange(self):
		for inputStr, start, end, expectedResultStr in self.rangeTestCases:
			input = self.factory.parse(inputStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Range(transf.traverse.Map(transf.rewrite.Rule('x', 'X(x)')), start, end)(input)
			
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
