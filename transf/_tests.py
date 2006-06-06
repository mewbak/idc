#!/usr/bin/env python
'''Unit tests for the transformation package.'''


import unittest

import aterm.factory

import transf
from transf import *
from transf.exception import *
from transf.base import *
from transf.combine import *
from transf.rewrite import *
from transf.traverse import *
from transf.unify import *

from transf.arith import *


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


class TestCombine(TestMixin, unittest.TestCase):
	
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
		self._testTransf(base.ident, self.identTestCases)

	def testFail(self):
		self._testTransf(base.fail, self.failTestCases)
	
	def testNot(self):
		self._testTransf(Not(base.ident), self.failTestCases)
		self._testTransf(Not(base.fail), self.identTestCases)
	
	def testTry(self):
		self._testTransf(Try(base.ident), self.identTestCases)
		self._testTransf(Try(base.fail), self.identTestCases)

	def testChoice(self):
		self._testTransf(Choice(base.ident, base.ident), self.identTestCases)
		self._testTransf(Choice(base.ident, base.fail), self.identTestCases)
		self._testTransf(Choice(fail, ident), self.identTestCases)
		self._testTransf(Choice(fail, fail), self.failTestCases)
		
	def testComposition(self):
		self._testTransf(Composition(ident, ident), self.identTestCases)
		self._testTransf(Composition(ident, fail), self.failTestCases)
		self._testTransf(Composition(fail, ident), self.failTestCases)
		self._testTransf(Composition(fail, fail), self.failTestCases)


class TestMatch(TestMixin, unittest.TestCase):
	
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
		self._testMatchTransf(match.Int(1), '1')

	def testReal(self):
		self._testMatchTransf(match.Real(0.1), '0.1')

	def testStr(self):
		self._testMatchTransf(match.Str("a"), '"a"')

	def testNil(self):
		self._testMatchTransf(match.nil, '[]')
	
	def testCons(self):
		self._testMatchTransf(match.Cons(match.Int(1),match.nil), '[1]')
	
	def testList(self):
		self._testMatchTransf(match.List([match.Int(1),match.Int(2)]), '[1,2]')
		self._testMatchTransf(match._[()], '[]')
		self._testMatchTransf(match._[1], '[1]')
		self._testMatchTransf(match._[1,2], '[1,2]')
	
	def testAppl(self):
		self._testMatchTransf(match.Appl(match.Str("C"),match.nil), 'C')
		self._testMatchTransf(match._.C(), 'C')
		self._testMatchTransf(match._.C(1), 'C(1)')
		self._testMatchTransf(match._.C(1,2), 'C(1,2)')


class TestTraverse(TestMixin, unittest.TestCase):

	mapTestCases = (
		[ident, fail, Rule('x', 'X(x)'), match.Pattern('1')],
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
		[ident, fail, Rule('x', 'X(x)'), match.Pattern('2')],
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
		[ident, fail, Rule('x', 'X(x)')],
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
		[ident, fail, Rule('x', 'X(x)')],
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
		[ident, fail, Try(Rule('f(x,y)', 'X(x,y)'))],
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
		self._testTransf(Split(match.Pattern('X')), self.spitTestCases)

	# TODO: testInnerMost


class TestUnify(TestMixin, unittest.TestCase):

	foldrTestCases = (
		('[1,2,3]', '6'),
	)
	
	def testFoldr(self):
		self._testTransf(
			Foldr(build.Int(0), Add),
			self.foldrTestCases
		)

	crushTestCases = (
		('[1,2]', '[1,[2,[]]]'),
		('C(1,2)', '[1,[2,[]]]'),
	)
	
	def testCrush(self):
		self._testTransf(Crush(ident, lambda x,y: build.List([x, y]), ident), self.crushTestCases)

	collectAllTestCases = (
		('1', '[1]'),
		('[1,2]', '[1,2]'),
		('C(1,2)', '[1,2]'),
		('[[1,2],C(3,4)]', '[1,2,3,4]'),
		('C([1,2],C(3,4))', '[1,2,3,4]'),
	)
	
	def testCollectAll(self):
		self._testTransf(
			CollectAll(match.AnInt()), 
			self.collectAllTestCases
		)
	

class TestArith(TestMixin, unittest.TestCase):

	addTestCases = (
		('[1,2]', '3'),
	)

	def testAdd(self):
		self._testTransf(
			Add(project.first, project.second), 
			self.addTestCases
		)


TestStub = Ident


class TestParse(TestMixin, unittest.TestCase):

	parseTestCases = [
		'id',
		'fail',
		'id ; fail',
		'id + fail',
		'id + fail ; id',
		'(id + fail) ; id',
		'?1',
		'?0.1',
		'?"s"',
		'?[]',
		'?[1,2]',
		'?C',
		'?C(1,2)',
		'?_',
		'?_(_,_)',
		'?x',
		'?f(x,y)',
		'!1',
		'!0.1',
		'!"s"',
		'![]',
		'![1,2]',
		'!C',
		'!C(1,2)',
		'!_',
		'!_(_,_)',
		'!x',
		'!f(x,y)',
		'?C(<id>,<fail>)',
		'!C(<id>,<fail>)',
		'ident',
		'TestStub()',
		'transf.base.Ident()',
		'( C(x,y) -> D(y,x) )',
		'{ C(x,y) -> D(y,x) }',
		'{x, y: id }',
		'<id> 123',
		'id => 123',
		'<id> 1 => 123',
		'!"," => sep',
		'where(!"," => sep)',
		'where( !"," => sep ); id',
		'{ sep : where( !"," => sep ); id }',
		'~C(1, <id>)',
	]
	
	def testAST(self):
		for input in self.parseTestCases:
			parser = parse._parser(input)
			parser.transf()
			ast = parser.getAST()
	
	def testParse(self):
		for input in self.parseTestCases:
			output = repr(parse.Transf(input))


if __name__ == '__main__':
	if __debug__:
		unittest.main()
	else:
		import hotshot
		filename = "transf.prof"
		prof = hotshot.Profile(filename, lineevents=0)
		prof.runcall(unittest.main)
		prof.close()

		
