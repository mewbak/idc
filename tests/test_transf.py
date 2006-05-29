#!/usr/bin/env python


import unittest

import aterm

from transf import *


class TestMixin:
	
	def setUp(self):
		self.factory = aterm.Factory()

	def _testTransf(self, transf, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			try:
				result = transf(term)
			except Failure:
				result = self.factory.parse('FAILURE')
			
			self.failUnlessEqual(result, expectedResult)

	def _testMetaTransf(self, metaTransf, testCases):
		result = []
		operands, rest = testCases
		for termStr, expectedResultStrs in rest.iteritems():
			for operand, expectedResultStr in zip(operands, expectedResultStrs):
				self._testTransf(metaTransf(operand), [(termStr, expectedResultStr)])


class TestCombinators(TestMixin, unittest.TestCase):
	
	annotatorTestCases = [
		('1', '1{Path,[]}'),
		('[1,2]', '[1{Path,[0]},2{Path,[1]}]{Path,[]}'),
		('C(1,2)', 'C(1{Path,[0]},2{Path,[1]}){Path,[]}'),
	]
	
	termsInputs = [
		'1',
		'0.1',
		'"s"',
		'[1,2]',
		'C(1,2)',
		'_',
		'x',
	]
		
	identTestCases = [(term, term) for term in termsInputs]
	failTestCases = [(term, 'FAILURE') for term in termsInputs]

	def testIdent(self):
		self._testTransf(Ident(), self.identTestCases)

	def testFail(self):
		self._testTransf(Fail(), self.failTestCases)
	
	def testNot(self):
		self._testTransf(Not(Ident()), self.failTestCases)
		self._testTransf(Not(Fail()), self.identTestCases)
	
	def testTry(self):
		self._testTransf(Try(Ident()), self.identTestCases)
		self._testTransf(Try(Fail()), self.identTestCases)

	def testChoice(self):
		self._testTransf(Choice(Ident(), Ident()), self.identTestCases)
		self._testTransf(Choice(Ident(), Fail()), self.identTestCases)
		self._testTransf(Choice(Fail(), Ident()), self.identTestCases)
		self._testTransf(Choice(Fail(), Fail()), self.failTestCases)
		
	def testComposition(self):
		self._testTransf(Composition(Ident(), Ident()), self.identTestCases)
		self._testTransf(Composition(Ident(), Fail()), self.failTestCases)
		self._testTransf(Composition(Fail(), Ident()), self.failTestCases)
		self._testTransf(Composition(Fail(), Fail()), self.failTestCases)


class TestTerm(TestMixin, unittest.TestCase):
	
	termInputs = [
		'0',
		'1',
		'2',
		'0.0',
		'0.1',
		'0.2',
		'""',
		'"a"',
		'"b"',
		'[]',
		'[1]',
		'[1,2]',
		'[1,*]',
		'[1,*x]',
		'C',
		'C(1)',
		'C(1,*)',
		'C(1,*a)',
		'D',
		'_',
		'x',
		'y',
	]
	
	def _testMatchTransf(self, transf, *matchStrs):
		testCases = []
		for termStr in self.termInputs:
			for matchStr in matchStrs:
				if matchStr == termStr:
					resultStr = termStr
				else:
					resultStr = 'FAILURE'
				testCases.append((termStr, resultStr))
		self._testTransf(transf, testCases)
					
	def testInt(self):
		self._testMatchTransf(Int(1), '1')

	def testReal(self):
		self._testMatchTransf(Real(0.1), '0.1')

	def testStr(self):
		self._testMatchTransf(Str("a"), '"a"')

	def testNil(self):
		self._testMatchTransf(Nil(), '[]')
	
	def testCons(self):
		self._testMatchTransf(Cons(Int(1), Nil()), '[1]')
	
	def testAppl(self):
		self._testMatchTransf(Appl(Str("C"), Nil()), 'C')


class TestTraversers(TestMixin, unittest.TestCase):

	mapTestCases = (
		[Ident(), Fail(), Rule('x', 'X(x)'), Match('1')],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', 'FAILURE', '[X(1)]', '[1]'],
			'[1,2]': ['[1,2]', 'FAILURE', '[X(1),X(2)]', 'FAILURE'],
			'[1,*]': ['[1,*]', 'FAILURE', '[X(1),*]', '[1,*]'],
			'[1,*x]': ['[1,*x]', 'FAILURE', '[X(1),*x]', '[1,*x]'],
		}
	)
		
	def testMap(self):
		self._testMetaTransf(Map, self.mapTestCases)

	# TODO: testFetch
	# TODO: testFilter
	
	allTestCases = (
		[Ident(), Fail(), Rule('x', 'X(x)')],
		{
			'A()': [
				'A()', 
				'A()', 
				'A()',
			],
			'A(B,C)': [
				'A(B,C))', 
				'FAILURE', 
				'A(X(B),X(C))',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))',
				'FAILURE', 
				'A(X(B(C,D)),X(E(F,G)))', 
			],
		}
	)
	
	def testAll(self):
		self._testMetaTransf(All, self.allTestCases)	

	bottomUpTestCases = (
		[Ident(), Fail(), Rule('x', 'X(x)')],
		{
			'A()': [
				'A()', 
				'FAILURE', 
				'X(A())',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))', 
				'FAILURE', 
				'X(A(X(B(X(C),X(D))),X(E(X(F),X(G)))))',
			],
		}
	)
	
	def testBottomUp(self):
		self._testMetaTransf(BottomUp, self.bottomUpTestCases)

	topDownTestCases = (
		[Ident(), Fail(), Try(Rule('f(x,y)', 'X(x,y)'))],
		{
			'A()': [
				'A()', 
				'FAILURE', 
				'A()',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))', 
				'FAILURE', 
				'X(X(C,D),X(F,G))',
			],
		}
	)
	
	def testTopdown(self):
		self._testMetaTransf(TopDown, self.topDownTestCases)

	spitTestCases = (
		('[1,2,3]', 'FAILURE'),
		('[X,1,2,3]', '[[],X,[1,2,3]]'),
		('[1,X,2,3]', '[[1,],X,[2,3]]'),
		('[1,2,X,3]', '[[1,2,],X,[3]]'),
		('[1,2,3,X]', '[[1,2,3],X,[]]'),
	)

	def testSplit(self):
		self._testTransf(Split(Match('X')), self.spitTestCases)

	# TODO: testInnerMost


if __name__ == '__main__':
	unittest.main()