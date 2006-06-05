#!/usr/bin/env python


import unittest

import aterm.factory

from transf.exception import *
from transf.base import *
#from transf.scope import *

from transf.combine import *
from transf.project import *
#from transf.match import *
#from transf.build import *
from transf.rewrite import *
from transf.traverse import *
from transf.unify import *

#from transf.annotation import *

from transf.arith import *
#from transf.lists import *
#from transf.strings import *


class TestMixin:
	
	def setUp(self):
		self.factory = aterm.factory.Factory()

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
		self._testTransf(combine.Ident(), self.identTestCases)

	def testFail(self):
		self._testTransf(combine.Fail(), self.failTestCases)
	
	def testNot(self):
		self._testTransf(Not(combine.Ident()), self.failTestCases)
		self._testTransf(Not(combine.Fail()), self.identTestCases)
	
	def testTry(self):
		self._testTransf(Try(combine.Ident()), self.identTestCases)
		self._testTransf(Try(combine.Fail()), self.identTestCases)

	def testChoice(self):
		self._testTransf(Choice(combine.Ident(), combine.Ident()), self.identTestCases)
		self._testTransf(Choice(combine.Ident(), combine.Fail()), self.identTestCases)
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
			if termStr in matchStrs:
				resultStr = termStr
			else:
				resultStr = 'FAILURE'
			testCases.append((termStr, resultStr))
		self._testTransf(transf, testCases)
					
	def testInt(self):
		self._testMatchTransf(match.MatchInt(1), '1')

	def testReal(self):
		self._testMatchTransf(match.MatchReal(0.1), '0.1')

	def testStr(self):
		self._testMatchTransf(match.MatchStr("a"), '"a"')

	def testNil(self):
		self._testMatchTransf(match.MatchNil(), '[]')
	
	def testCons(self):
		self._testMatchTransf(TraverseCons(match.MatchInt(1),match.MatchNil()), '[1]')
	
	def testList(self):
		self._testMatchTransf(TraverseList([match.MatchInt(1),match.MatchInt(2)]), '[1,2]')
	
	def testAppl(self):
		self._testMatchTransf(TraverseAppl(match.MatchStr("C"),match.MatchNil()), 'C')


class TestTraversers(TestMixin, unittest.TestCase):

	mapTestCases = (
		[Ident(), Fail(), Rule('x', 'X(x)'), Match('1')],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', 'FAILURE', '[X(1)]', '[1]'],
			'[1,2]': ['[1,2]', 'FAILURE', '[X(1),X(2)]', 'FAILURE'],
			#'[1,*]': ['[1,*]', 'FAILURE', '[X(1),*]', '[1,*]'],
			#'[1,*x]': ['[1,*x]', 'FAILURE', '[X(1),*x]', '[1,*x]'],
		}
	)
		
	def testMap(self):
		self._testMetaTransf(Map, self.mapTestCases)

	# TODO: testFetch

	filterTestCases = (
		[Ident(), Fail(), Rule('x', 'X(x)'), Match('2')],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', '[]', '[X(1)]', '[]'],
			'[1,2]': ['[1,2]', '[]', '[X(1),X(2)]', '[2]'],
			'[1,2,3]': ['[1,2,3]', '[]', '[X(1),X(2),X(3)]', '[2]'],
		}
	)
		
	def testFilter(self):
		self._testMetaTransf(Filter, self.filterTestCases)
	
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
		# FIXME: move this away from here
		from ir.transfs import Split
		self._testTransf(Split(Match('X')), self.spitTestCases)

	# TODO: testInnerMost


class TestUnifiers(TestMixin, unittest.TestCase):

	foldrTestCases = (
		('[1,2,3]', '6'),
	)
	
	def testFoldr(self):
		self._testTransf(Foldr(build.BuildInt(0),Add(First(),Second())), self.foldrTestCases)

	crushTestCases = (
		('[1,2]', '[1,[2,[]]]'),
		('C(1,2)', '[1,[2,[]]]'),
	)
	
	def testCrush(self):
		self._testTransf(Crush(Ident(),Ident(), Ident()), self.crushTestCases)

	collectAllTestCases = (
		('1', '[1]'),
		('[1,2]', '[1,2]'),
		('C(1,2)', '[1,2]'),
		('[[1,2],C(3,4)]', '[1,2,3,4]'),
		('C([1,2],C(3,4))', '[1,2,3,4]'),
	)
	
	def testCollectAll(self):
		self._testTransf(CollectAll(match.IsInt()), self.collectAllTestCases)
	

class TestArith(TestMixin, unittest.TestCase):

	addTestCases = (
		('[1,2]', '3'),
	)

	def testAdd(self):
		self._testTransf(Add(First(),Second()), self.addTestCases)


if __name__ == '__main__':
	if __debug__:
		unittest.main()
	else:
		import hotshot
		filename = "transf.prof"
		prof = hotshot.Profile(filename, lineevents=0)
		prof.runcall(unittest.main)
		prof.close()

		
