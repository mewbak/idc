#!/usr/bin/env python
'''Unit tests for the transformation package.'''


import unittest

import antlr

import aterm.factory

from transf.lib import *
from transf.lib.base import ident, fail


class TestMixin:

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
		'C',
		'C(1)',
		'D',
	]

	def setUp(self):
		self.factory = aterm.factory.factory

	def _testTransf(self, transf, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = transf(term)
			except exception.Failure:
				result = self.factory.parse('FAILURE')

			self.failUnless(isinstance(result, aterm.term.Term),
				msg = "not a term: %s -> %s (!= %s)" % (term, result, expectedResult)
			)

			self.failUnless(expectedResult.isEqual(result),
				msg = "%s -> %s (!= %s)" %(term, result, expectedResult)
			)

	def _testMetaTransf(self, metaTransf, testCases):
		result = []
		operands, rest = testCases
		for termStr, expectedResultStrs in rest.iteritems():
			for operand, expectedResultStr in zip(operands, expectedResultStrs):
				self._testTransf(metaTransf(operand), [(termStr, expectedResultStr)])


class TestCombine(TestMixin, unittest.TestCase):

	identTestCases = [(term, term) for term in TestMixin.termInputs]
	failTestCases = [(term, 'FAILURE') for term in TestMixin.termInputs]
	xxxTestCases = [(term, 'X') for term in TestMixin.termInputs]

	def testIdent(self):
		self._testTransf(ident, self.identTestCases)
		self._testTransf(parse.Transf('id'), self.identTestCases)

	def testFail(self):
		self._testTransf(fail, self.failTestCases)
		self._testTransf(parse.Transf('fail'), self.failTestCases)

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
			2: parse.Rule('_ -> X'),
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
				self.fail(msg = "%s => ? != %s" % (args, result))

	def testNot(self):
		func = lambda x: not x
		self._testCombination(combine._Not, 1, func)
		self._testCombination(combine.Not, 1, func)

	def testTry(self):
		func = lambda x: x or 1
		self._testCombination(combine._Try, 1, func)
		self._testCombination(combine.Try, 1, func)

	def testChoice(self):
		func = lambda x, y: x or y
		self._testCombination(combine._Choice, 2, func)
		self._testCombination(combine.Choice, 2, func)
		self._testCombination(parse.Meta('x, y: x + y'), 2, func)

	def testComposition(self):
		func = lambda x, y: x and y and max(x, y) or 0
		self._testCombination(combine._Composition, 2, func)
		self._testCombination(combine.Composition, 2, func)
		self._testCombination(parse.Meta('x, y: x ; y'), 2, func)

	def testGuardedChoice(self):
		func = lambda x, y, z: (x and y and max(x, y) or 0) or (not x and z)
		self._testCombination(combine._GuardedChoice, 3, func)
		self._testCombination(combine.GuardedChoice, 3, func)
		self._testCombination(parse.Meta('x, y, z: x < y + z'), 3, func)

	def testIf(self):
		func = lambda x, y: (x and y) or (not x)
		self._testCombination(combine._If, 2, func)
		self._testCombination(combine.If, 2, func)
		self._testCombination(parse.Meta('x, y: if x then y end'), 2, func)

	def testIfElse(self):
		func = lambda x, y, z: (x and y) or (not x and z)
		self._testCombination(combine._IfElse, 3, func)
		self._testCombination(combine.IfElse, 3, func)
		self._testCombination(parse.Meta('x, y, z: if x then y else z end'), 3, func)


class TestMatch(TestMixin, unittest.TestCase):

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
		self._testMatchTransf(parse.Transf('?1'), '1')

	def testReal(self):
		self._testMatchTransf(match.Real(0.1), '0.1')
		self._testMatchTransf(parse.Transf('?0.1'), '0.1')

	def testStr(self):
		self._testMatchTransf(match.Str("a"), '"a"')
		self._testMatchTransf(parse.Transf('?"a"'), '"a"')

	def testNil(self):
		self._testMatchTransf(match.nil, '[]')
		self._testMatchTransf(parse.Transf('?[]'), '[]')

	def testCons(self):
		self._testMatchTransf(match.Cons(match.Int(1),match.nil), '[1]')
		self._testMatchTransf(parse.Transf('?[1]'), '[1]')

	def testList(self):
		self._testMatchTransf(match.List([match.Int(1),match.Int(2)]), '[1,2]')
		self._testMatchTransf(match._[()], '[]')
		self._testMatchTransf(match._[1], '[1]')
		self._testMatchTransf(match._[1,2], '[1,2]')
		self._testMatchTransf(parse.Transf('?[1,2]'), '[1,2]')

	def testAppl(self):
		self._testMatchTransf(match.Appl("C", ()), 'C')
		self._testMatchTransf(match.ApplCons(match.Str("C"), match.nil), 'C')
		self._testMatchTransf(match._.C(), 'C')
		self._testMatchTransf(match._.C(1), 'C(1)')
		self._testMatchTransf(match._.C(1,2), 'C(1,2)')
		self._testMatchTransf(parse.Transf('?C()'), 'C')
		self._testMatchTransf(parse.Transf('?C(1)'), 'C(1)')
		self._testMatchTransf(parse.Transf('?C(1,2)'), 'C(1,2)')


class TestTraverse(TestMixin, unittest.TestCase):

	allTestCases = (
		[ident, fail, parse.Rule('x -> X(x)')],
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
		[ident, fail, parse.Rule('X -> Y')],
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
		}
	)

	def testOne(self):
		self._testMetaTransf(traverse.One, self.oneTestCases)

	someTestCases = (
		[ident, fail, parse.Rule('X -> Y')],
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
		}
	)

	def testSome(self):
		self._testMetaTransf(traverse.Some, self.someTestCases)

	bottomUpTestCases = (
		[ident, fail, parse.Rule('x -> X(x)')],
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
		[ident, fail, combine.Try(parse.Rule('f(x,y) -> X(x,y)'))],
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

	# TODO: testInnerMost


class TestProject(TestMixin, unittest.TestCase):

	subtermsTestCases = (
		('1', '[]'),
		('0.1', '[]'),
		('"a"', '[]'),
		('[]', '[]'),
		('[1]', '[1]'),
		('[1,2]', '[1,2]'),
		('C', '[]'),
		('C(1)', '[1]'),
		('C(1,2)', '[1,2]'),
	)

	def testSubterms(self):
		self._testTransf(project.subterms, self.subtermsTestCases)

	fetchTestCases = (
		[ident, fail, parse.Rule('X -> Y')],
		{
			'[]': ['FAILURE', 'FAILURE', 'FAILURE'],
			'[X]': ['X', 'FAILURE', 'Y'],
			'[X,A]': ['X', 'FAILURE', 'Y'],
			'[A,X]': ['A', 'FAILURE', 'Y'],
			'[X{1},X{2}]': ['X{1}', 'FAILURE', 'Y'],
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
			unify.CollectAll(match.anInt),
			self.collectAllTestCases
		)


class TestAnno(TestMixin, unittest.TestCase):

	def _testAnnoTransf(self, Transf, testCases):
		for input, label, values, output in testCases:
			transf = Transf(label, *map(build.Term, values))
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
		'?C(v@<id>,<fail>)',
		'base.ident',
		'TestStub()',
		'base.Ident()',
		'( C(x,y) -> D(y,x) )',
		'{ C(x,y) -> D(y,x) }',
		'<id> 123',
		'id; ?123',
		'id => a',
		'<id> 1 ; ?123',
		'!"," => sep',
		'Where(!"," => sep)',
		'Where( !"," => sep ); id',
		'with sep in Where( !"," => sep ); id end',
		'~C(1, <id>)',
		'!1{A,B,C}',
		'if ?c then !x end',
		'if ?c then !x else !y end',
		'?1 < !2 + !3',
		'?1 < !2 + !3 + !4',
		'?1 + !2 + !3 + !4',
		'switch !x case 1: !A case 2: !B else: !C end',
		'!1 / a \\ !2',
		'!1 / a \\ \\ b / !2',
		'=a',
		#'/a',
		'with a, b=!1, c[], d[] = e in id end',
	]

	def testParse(self):
		for input in self.parseTestCases:
			try:
				parser = parse._parser(input)
				parser.transf()
			except:
				print input
				raise
			ast = parser.getAST()

			#print "INPUT:", input
			#print "AST:", ast.toStringTree()
			#import antlraterm
			#term = antlraterm.Walker().aterm(ast)
			#print "ATERM:", term

			try:
				output = repr(parse.Transf(input))
			except:
				print input
				if ast is not None:
					print ast.toStringTree()
				raise
			#print "OUTPUT:", output
			#print


class TestPath(TestMixin, unittest.TestCase):

	def testAnnotate(self):
		self._testTransf(
			path.annotate,
			(
				('1', '1{Path([])}'),
				('[1,2]', '[1{Path([0])},2{Path([1])}]{Path([])}'),
				('C(1,2)', 'C(1{Path([0])},2{Path([1])}){Path([])}'),
				('[[[]]]', '[[[]{Path([0,0])}]{Path([0])}]{Path([])}'),
				('C(C(C))', 'C(C(C{Path([0,0])}){Path([0])}){Path([])}'),
				('[[1],[2]]', '[[1{Path([0,0])}]{Path([0])},[2{Path([0,1])}]{Path([1])}]{Path([])}'),
				('C(C(1),C(2))', 'C(C(1{Path([0,0])}){Path([0])},C(2{Path([0,1])}){Path([1])}){Path([])}'),
			)
		)

	def checkTransformation(self, metaTransf, testCases):
		for termStr, pathStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)

			result = metaTransf(_path)(term)

			self.failUnlessEqual(result, expectedResult)

	projectTestCases = [
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

	def testProject(self):
		self.checkTransformation(
			path.Project,
			self.projectTestCases
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

	def testSubTerm(self):
		self.checkTransformation(
			lambda p: path.SubTerm(parse.Rule('x -> X(x)'), p),
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

			result = path.Range(lists.Map(parse.Rule('x -> X(x)')), start, end)(input)

			self.failUnlessEqual(result, expectedResult)


class TestLists(TestMixin, unittest.TestCase):

	mapTestCases = (
		[ident, fail, parse.Rule('x -> X(x)'), match.Int(1)],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', 'FAILURE', '[X(1)]', '[1]'],
			'[1,2]': ['[1,2]', 'FAILURE', '[X(1),X(2)]', 'FAILURE'],
		}
	)

	def testMap(self):
		self._testMetaTransf(lists.Map, self.mapTestCases)

	filterTestCases = (
		[ident, fail, parse.Rule('x -> X(x)'), match.Int(2)],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', '[]', '[X(1)]', '[]'],
			'[1,2]': ['[1,2]', '[]', '[X(1),X(2)]', '[2]'],
			'[1,2,3]': ['[1,2,3]', '[]', '[X(1),X(2),X(3)]', '[2]'],
		}
	)

	def testFilter(self):
		self._testMetaTransf(lists.Filter, self.filterTestCases)
		self._testMetaTransf(lists.FilterR, self.filterTestCases)

	# TODO: testFetch

	def testSplit(self):
		self._testTransf(
			lists.Split(parse.Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[],[A,B,C]]'),
				('[A,X,B,C]', '[[A],[B,C]]'),
				('[A,B,X,C]', '[[A,B],[C]]'),
				('[A,B,C,X]', '[[A,B,C],[]]'),
			)
		)

	def testSplitBefore(self):
		self._testTransf(
			lists.SplitBefore(parse.Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[],[Y,A,B,C]]'),
				('[A,X,B,C]', '[[A],[Y,B,C]]'),
				('[A,B,X,C]', '[[A,B],[Y,C]]'),
				('[A,B,C,X]', '[[A,B,C],[Y]]'),
			)
		)

	def testSplitAfter(self):
		self._testTransf(
			lists.SplitAfter(parse.Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[Y],[A,B,C]]'),
				('[A,X,B,C]', '[[A,Y],[B,C]]'),
				('[A,B,X,C]', '[[A,B,Y],[C]]'),
				('[A,B,C,X]', '[[A,B,C,Y],[]]'),
			)
		)

	def testSplitKeep(self):
		self._testTransf(
			lists.SplitKeep(parse.Rule('X -> Y')),
			(
				('[A,B,C,D]', 'FAILURE'),
				('[X,A,B,C,D]', '[[],Y,[A,B,C,D]]'),
				('[A,X,B,C,D]', '[[A],Y,[B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],Y,[C,D]]'),
				('[A,B,C,X,D]', '[[A,B,C],Y,[D]]'),
				('[A,B,C,D,X]', '[[A,B,C,D],Y,[]]'),
			)
		)

	def testSplitAll(self):
		self._testTransf(
			lists.SplitAll(parse.Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],[C,D]]'),
				('[A,X,B,X,C]', '[[A],[B],[C]]'),
				('[X,A,B,C,X]', '[[],[A,B,C],[]]'),
			)
		)

	def _testSplitAllBefore(self):
		self._testTransf(
			lists.SplitAllBefore(parse.Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],[Y,A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],[Y,C,D]]'),
				('[A,X,B,X,C]', '[[A],[Y,B],[Y,C]]'),
				('[X,A,B,C,X]', '[[],[Y,A,B,C],[Y]]'),
			)
		)

	def testSplitAllAfter(self):
		self._testTransf(
			lists.SplitAllAfter(parse.Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[Y],[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B,Y],[C,D]]'),
				('[A,X,B,X,C]', '[[A,Y],[B,Y],[C]]'),
				('[X,A,B,C,X]', '[[Y],[A,B,C,Y],[]]'),
			)
		)

	def testSplitAllKeep(self):
		self._testTransf(
			lists.SplitAllKeep(parse.Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],Y,[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],Y,[C,D]]'),
				('[A,X,B,X,C]', '[[A],Y,[B],Y,[C]]'),
				('[X,A,B,C,X]', '[[],Y,[A,B,C],Y,[]]'),
			)
		)


if __name__ == '__main__':
	if __debug__:
		unittest.main()
	else:
		import hotshot
		filename = "prof"
		prof = hotshot.Profile(filename, lineevents=0)
		prof.runcall(unittest.main)
		prof.close()

