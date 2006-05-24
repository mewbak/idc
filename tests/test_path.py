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
	]
	
	def testAnnotator(self):
		for termStr, expectedResultStr in self.annotatorTestCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Annotator.annotate(term)
			
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
	]
	
	def testEvaluator(self):
		for termStr, pathStr, expectedResultStr in self.evaluatorTestCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Evaluator.evaluate(term, _path)
			
			self.failUnlessEqual(result, expectedResult)
	
	applyTestCases = [
		('1', '[]', 'X(1)'),
		('[1,2]', '[]', 'X([1,2])'),
		('[1,2]', '[0]', '[X(1),2]'),
		('[1,2]', '[1]', '[1,X(2)]'),
		('C(1,2)', '[]', 'X(C(1,2))'),
		('C(1,2)', '[0]', 'C(X(1),2)'),
		('C(1,2)', '[1]', 'C(1,X(2))'),
		('A([B,C],[D,E])', '[1,0]', 'A([B,C],[X(D),E])'),
		('A([B,C],[D,E])', '[0,1]', 'A([B,X(C)],[D,E])'),
	]	
	
	def testApply(self):
		import transformations
		
		for termStr, pathStr, expectedResultStr in self.applyTestCases:
			term = self.factory.parse(termStr)
			#_path = self.factory.parse(pathStr)
			_path = eval(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			result = path.Apply(_path, transformations.Rule('x', 'X(x)'))(term)
			
			self.failUnlessEqual(result, expectedResult)



if __name__ == '__main__':
	unittest.main()
