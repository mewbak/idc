#!/usr/bin/env python
'''Unit tests for the transformation package.'''


import unittest

import antlr

import aterm.factory

from transf import *

from transf.base import ident, fail
from transf.combine import Try
from transf.rewrite import Rule


class TestMixin:
	
	def setUp(self):
		self.factory = aterm.factory.Factory()

	def _testTransf(self, transf, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			try:
				result = transf(term)
			except exception.Failure:
				result = self.factory.parse('FAILURE')
			
			self.failUnlessEqual(result, expectedResult, 
				msg = "%r -> %r (!= %r)" %(term, result, expectedResult)
			)

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
	xxxTestCases = [(term, 'X') for term in termsInputs]

	def testIdent(self):
		self._testTransf(ident, self.identTestCases)

	def testFail(self):
		self._testTransf(fail, self.failTestCases)
	
	unaryTestCases = [
		[0], [1], [2],
	]
	
	binaryTestCases = [
		[0, 0], [0, 1], [0, 2], 
		[1, 0], [1, 1], [1, 2],
		[2, 0], [2, 1], [2, 2],
	]
	
	ternaryTestCases = [
		[0, 0, 0], [0, 0, 1], [0, 0, 2],
		[0, 1, 0], [0, 1, 1], [0, 1, 2],
		[0, 2, 0], [0, 2, 1], [0, 2, 2],
		[1, 0, 0], [1, 0, 1], [1, 0, 2],
		[1, 1, 0], [1, 1, 1], [1, 1, 2],
		[1, 2, 0], [1, 2, 1], [1, 2, 2],
		[2, 0, 0], [2, 0, 1], [2, 0, 2],
		[2, 1, 0], [2, 1, 1], [2, 1, 2],
		[2, 2, 0], [2, 2, 1], [2, 2, 2],
	]

	def _testCombination(self, Transf, n, func):
		argTable = {
			0: fail,
			1: ident, 
			2: Rule('_', 'X'),
		}
		testCaseTable = {
			1: self.unaryTestCases, 
			2: self.binaryTestCases,
			3: self.ternaryTestCases,
		}
		resultTable = {
			0: self.failTestCases,
			1: self.identTestCases, 
			2: self.xxxTestCases,
		}
		testCases = testCaseTable[n]
		for args in testCases:
			transf = Transf(*map(argTable.get, args))
			result = int(func(*args))
			resultCases = resultTable[result]
			try:
				self._testTransf(transf, resultCases)
			except AssertionError:
				self.fail(msg = "%r => ? != %r" % (args, result))
	
	def testNot(self):
		func = lambda x: not x
		self._testCombination(combine.Not, 1, func)
	
	def testTry(self):
		func = lambda x: x or 1
		self._testCombination(combine._Try, 1, func)
		self._testCombination(combine.Try, 1, func)

	def testChoice(self):
		func = lambda x, y: x or y
		self._testCombination(combine._Choice, 2, func)
		self._testCombination(combine.Choice, 2, func)
		
	def testComposition(self):
		func = lambda x, y: x and y and max(x, y) or 0
		self._testCombination(combine._Composition, 2, func)
		self._testCombination(combine.Composition, 2, func)

	def testGuardedChoice(self):
		func = lambda x, y, z: (x and y and max(x, y) or 0) or (not x and z)
		self._testCombination(combine.GuardedChoice, 3, func)

	def testIfThen(self):
		func = lambda x, y: (x and y) or (not x)
		self._testCombination(combine.IfThen, 2, func)
		
	def testIfThenElse(self):
		func = lambda x, y, z: (x and y) or (not x and z)
		self._testCombination(combine.IfThenElse, 3, func)


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
		self._testMetaTransf(traverse.Map, self.mapTestCases)

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
		self._testMetaTransf(traverse.Filter, self.filterTestCases)

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
		self._testMetaTransf(traverse.All, self.allTestCases)	
	
	oneTestCases = (
		[ident, fail, Rule('X(*a)', 'Y(*a)')],
		{
			'1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'0.1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'"s"': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'X()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A(X)': ['A(X)', 'FAILURE', 'A(Y)'],
			'A(B,C)': ['A(B,C))', 'FAILURE', 'FAILURE'],
			'A(X,B)': ['A(X,B))', 'FAILURE', 'A(Y,B)'],
			'A(B,X)': ['A(B,X))', 'FAILURE', 'A(B,Y)'],
			'A(X,X)': ['A(X,X))', 'FAILURE', 'A(Y,X)'],
			'A(X(X,X))': ['A(X(X,X))', 'FAILURE', 'A(Y(X,X))'],
		}
	)
	
	def testOne(self):
		self._testMetaTransf(traverse.One, self.oneTestCases)	

	someTestCases = (
		[ident, fail, Rule('X(*a)', 'Y(*a)')],
		{
			'1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'0.1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'"s"': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'X()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A(X)': ['A(X)', 'FAILURE', 'A(Y)'],
			'A(B,C)': ['A(B,C))', 'FAILURE', 'FAILURE'],
			'A(X,B)': ['A(X,B))', 'FAILURE', 'A(Y,B)'],
			'A(B,X)': ['A(B,X))', 'FAILURE', 'A(B,Y)'],
			'A(X,X)': ['A(X,X))', 'FAILURE', 'A(Y,Y)'],
			'A(X(X,X))': ['A(X(X,X))', 'FAILURE', 'A(Y(X,X))'],
		}
	)
	
	def testSome(self):
		self._testMetaTransf(traverse.Some, self.someTestCases)	

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
		self._testMetaTransf(traverse.BottomUp, self.bottomUpTestCases)

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
		self._testMetaTransf(traverse.TopDown, self.topDownTestCases)

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


class TestProject(TestMixin, unittest.TestCase):

	fetchTestCases = (
		[ident, fail, Rule('X(*a)', 'Y(*a)')],
		{
			'[]': ['FAILURE', 'FAILURE', 'FAILURE'],
			'[X]': ['X', 'FAILURE', 'Y'],
			'[X,A]': ['X', 'FAILURE', 'Y'],
			'[A,X]': ['A', 'FAILURE', 'Y'],
			'[X(1),X(2)]': ['X(1)', 'FAILURE', 'Y(1)'],
		}
	)
	
	def testFetch(self):
		self._testMetaTransf(project.Fetch, self.fetchTestCases)
	

class TestUnify(TestMixin, unittest.TestCase):

	foldrTestCases = (
		('[1,2,3]', '6'),
	)
	
	def testFoldr(self):
		self._testTransf(
			unify.Foldr(build.Int(0), arith.Add),
			self.foldrTestCases
		)

	crushTestCases = (
		('[1,2]', '[1,[2,[]]]'),
		('C(1,2)', '[1,[2,[]]]'),
	)
	
	def testCrush(self):
		self._testTransf(
			unify.Crush(ident, lambda x,y: build.List([x, y]), ident), 
			self.crushTestCases
		)

	collectAllTestCases = (
		('1', '[1]'),
		('[1,2]', '[1,2]'),
		('C(1,2)', '[1,2]'),
		('[[1,2],C(3,4)]', '[1,2,3,4]'),
		('C([1,2],C(3,4))', '[1,2,3,4]'),
	)
	
	def testCollectAll(self):
		self._testTransf(
			unify.CollectAll(match.AnInt()), 
			self.collectAllTestCases
		)
	

class TestAnno(TestMixin, unittest.TestCase):

	def _testAnnoTransf(self, Transf, testCases):
		for input, label, values, output in testCases:
			transf = Transf(label, *map(build.Pattern, values))
			self._testTransf(transf, [(input, output)])
		
	setTestCases = (
		('X', "A", ['1'], 'X{A(1)}'),
		('X{B(2)}', "A", ['1'], 'X{A(1),B(2)}'),
		('X{A(1)}', "A", ['2'], 'X{A(2)}'),
		('X{A(1),B(2)}', "A", ['2'], 'X{A(2),B(2)}'),
		('X{B(1),A(2)}', "A", ['1'], 'X{B(1),A(1)}'),
	)

	def testSet(self):
		self._testAnnoTransf(annotation.Set, self.setTestCases)

	updateTestCases = (
		('X', "A", ['1'], 'FAILURE'),
		('X{B(2)}', "A", ['1'], 'FAILURE'),
		('X{A(1)}', "A", ['2'], 'X{A(2)}'),
		('X{A(1),B(2)}', "A", ['2'], 'X{A(2),B(2)}'),
		('X{B(1),A(2)}', "A", ['1'], 'X{B(1),A(1)}'),
	)

	def testUpdate(self):
		self._testAnnoTransf(annotation.Update, self.updateTestCases)

	getTestCases = (
		('X{A(1)}', "A", [], '1'),
		('X{A(1),B(2)}', "A", [], '1'),
		('X{B(1),A(2)}', "A", [], '2'),
		('X', "A", [], 'FAILURE'),
	)

	def testGet(self):
		self._testAnnoTransf(annotation.Get, self.getTestCases)

	delTestCases = (
		('X', "A", [], 'X'),
		('X{B(2)}', "A", [], 'X{B(2)}'),
		('X{A(1)}', "A", [], 'X'),
		('X{A(1),B(2)}', "A", [], 'X{B(2)}'),
		('X{B(1),A(2)}', "A", [], 'X{B(1)}'),
	)

	def testDel(self):
		self._testAnnoTransf(annotation.Del, self.delTestCases)


class TestArith(TestMixin, unittest.TestCase):

	addTestCases = (
		('[1,2]', '3'),
	)

	def testAdd(self):
		self._testTransf(
			arith.Add(project.first, project.second), 
			self.addTestCases
		)


TestStub = base.Ident


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
		'base.ident',
		'TestStub()',
		'base.Ident()',
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
		'!1{A,B,C}',
		'if ?c then !x end',
		'if ?c then !x else !y end',
		'let x=!X, y=!Y in ![x,y] end',
		'?1 < !2 + !3',
		'?1 < !2 + !3 + !4',
		'?1 + !2 + !3 + !4',
	]
	
	def testAST(self):
		for input in self.parseTestCases:
			parser = parse._parser(input)
			try:
				parser.transf()
			except antlr.ANTLRException, ex:
				self.fail(msg = "%r failed: %s" % (input, ex))
			ast = parser.getAST()
	
	def testParse(self):
		for input in self.parseTestCases:
			print input
			try:
				output = repr(parse.Transf(input))
			except antlr.ANTLRException, ex:
				self.fail(msg = "%r failed: %s" % (input, ex))
			print output


if __name__ == '__main__':
	if __debug__:
		unittest.main()
	else:
		import hotshot
		filename = "transf.prof"
		prof = hotshot.Profile(filename, lineevents=0)
		prof.runcall(unittest.main)
		prof.close()

		
