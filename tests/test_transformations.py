#!/usr/bin/env python


import unittest

import aterm

from transformations import *


def exxer(term):
	return term.factory.make('X(_)', term)

def greater_than_one(term):
	if term.getType() == aterm.INT and term.getValue() > 1:
		return term
	else:
		raise Failure


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.Factory()

	annotatorTestCases = [
		('1', '1{Path,[]}'),
		('[1,2]', '[1{Path,[0]},2{Path,[1]}]{Path,[]}'),
		('C(1,2)', 'C(1{Path,[0]},2{Path,[1]}){Path,[]}'),
	]
	
	def checkTransf(self, transformation, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)
			
			try:
				result = transformation(term)
			except Failure:
				result = self.factory.parse("FAILURE")
			
			self.failUnlessEqual(result, expectedResult)

	def checkMetaTransf(self, metaTransf, testCases):
		result = []
		for inputStr, rest in testCases.iteritems():
			for operand, expectedResultStr in rest:
				self.checkTransf(metaTransf(operand), [(inputStr, expectedResultStr)])

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
		self.checkTransf(Ident(), self.identTestCases)

	def testFail(self):
		self.checkTransf(Fail(), self.failTestCases)
	
	def testNot(self):
		self.checkTransf(Not(Ident()), self.failTestCases)
		self.checkTransf(Not(Fail()), self.identTestCases)
	
	def testTry(self):
		self.checkTransf(Try(Ident()), self.identTestCases)
		self.checkTransf(Try(Fail()), self.identTestCases)

	def testOr(self):
		self.checkTransf(Or(Ident(), Ident()), self.identTestCases)
		self.checkTransf(Or(Ident(), Fail()), self.identTestCases)
		self.checkTransf(Or(Fail(), Ident()), self.identTestCases)
		self.checkTransf(Or(Fail(), Fail()), self.failTestCases)
		
	def testAnd(self):
		self.checkTransf(And(Ident(), Ident()), self.identTestCases)
		self.checkTransf(And(Ident(), Fail()), self.failTestCases)
		self.checkTransf(And(Fail(), Ident()), self.failTestCases)
		self.checkTransf(And(Fail(), Fail()), self.failTestCases)

	listsInputs = [
		'[]',
		'[1]',
		'[1,2]',
		'[1,2,3]',
		'[1,2,*]',
		'[1,2,*x]',
	]

	listsExxerOutputs = [
		'[]',
		'[X(1)]',
		'[X(1),X(2)]',
		'[X(1),X(2),X(3)]',
		'[X(1),X(2),*]',
		'[X(1),X(2),*x]',
	]
	
	listsNotGreaterThanOneOutputs = [
		'[]',
		'[1]',
		'FAILURE',
		'FAILURE',
		'FAILURE',
		'FAILURE',
	]
	
	def testMap(self):
		self.checkTransf(
			Map(Ident()), 
			[(term, term) for term in self.listsInputs],
		)
		self.checkTransf(
			Map(Fail()), 
			[(term, term == '[]' and '[]' or 'FAILURE') for term in self.listsInputs],
		)
		self.checkTransf(
			Map(exxer),
			zip(self.listsInputs, self.listsExxerOutputs)
		)
		self.checkTransf(
			Map(Not(greater_than_one)),
			zip(self.listsInputs, self.listsNotGreaterThanOneOutputs)
		)
	
	bottomUpTestCases = {
		'A(B(C,D),E(F,G))': [
			(Ident(), 'A(B(C,D),E(F,G))'),
			(Fail(), 'FAILURE()'),
			(Rule('x', 'X(x)'), 'X(A(X(B(X(C),X(D))),X(E(X(F),X(G)))))')
		]
	}
	
	def testBottomUp(self):
		self.checkMetaTransf(BottomUp, self.bottomUpTestCases)

	# FIXME: write the remaining test cases


if __name__ == '__main__':
	unittest.main()
