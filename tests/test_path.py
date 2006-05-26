#!/usr/bin/env python


import unittest

import aterm
import path


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
	
	annotatorTestCases = [
		('1', '1{Path,[]}'),
		('[1,2]', '[1{Path,[0]},2{Path,[1]}]{Path,[]}'),
		('C(1,2)', 'C(1{Path,[0]},2{Path,[1]}){Path,[]}'),
		('[[[]]]', '[[[]{Path,[0,0]}]{Path,[0]}]{Path,[]}'),
		('C(C(C))', 'C(C(C{Path,[0,0]}){Path,[0]}){Path,[]}'),
		('[[1],[2]]', '[[1{Path,[0,0]}]{Path,[0]},[2{Path,[0,1]}]{Path,[1]}]{Path,[]}'),
		('C(C(1),C(2))', 'C(C(1{Path,[0,0]}){Path,[0]},C(2{Path,[0,1]}){Path,[1]}){Path,[]}'),
	]
	
	def testAnnotator(self):
		for termStr, expectedResultStr in self.annotatorTestCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Annotator()(term)
			
			self.failUnlessEqual(result, expectedResult)
			
			self.failUnless(result.isEquivalent(term))
			self.failUnless(term.isEquivalent(result))

	evaluatorTestCases = [
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
	
	def testEvaluator(self):
		for termStr, pathStr, expectedResultStr in self.evaluatorTestCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Evaluator(_path)(term)
			
			self.failUnlessEqual(result, expectedResult)
	
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
		import transformations
		
		for termStr, pathStr, expectedResultStr in self.pathTestCases:
			term = self.factory.parse(termStr)
			#_path = self.factory.parse(pathStr)
			_path = eval(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Path(transformations.Rule('x', 'X(x)'), _path)(term)
			
			self.failUnlessEqual(result, expectedResult)

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


if __name__ == '__main__':
	unittest.main()
