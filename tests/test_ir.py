#!/usr/bin/env python


import unittest

import aterm
import box
import ir


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
	
	checkerTestCases = [
		("module", "Module([])", True),
		("module", "XXX", False),
	]
	
	def testChecker(self):
		checker = ir.Checker(self.factory)

		for methodName, inputStr, expectedOutput in self.checkerTestCases:
			input = self.factory.parse(inputStr)
		
			try:
				getattr(checker, methodName)(input)
				output = True
			except ir.Failure:
				output = False
			
			self.failUnlessEqual(
					output, expectedOutput, 
					msg = '%s(%s) = %r (%r expected)' % (methodName, inputStr, output, expectedOutput)
			)

	prettyPrinterTestCases = {
		'expr': [
			('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', '1 + x'),
		],
		
		'stmt': [
			('Label("label")', 'label:'),
			('Asm("ret",[])', 'asm("ret");'),
			('Asm("mov",[Sym("ax"), Lit(Int(32,Signed),1234)])', 'asm("mov", ax, 1234);'),
		],
		
		
	}
	
	def testPrettyPrinter(self):
		for methodName, subTestCases in self.prettyPrinterTestCases.iteritems():
			for inputStr, expectedOutput in subTestCases:
				input = self.factory.parse(inputStr)
			
				printer = ir.PrettyPrinter(self.factory)
				boxes = getattr(printer, methodName)(input)
				
				output = box.box2text(boxes)
				
				self.failUnlessEqual(output, expectedOutput)

	exprTestCases = [
		('Sym("x")', None, lambda x: -x, 'Unary(Neg(32),Sym("x"))'),
		('Sym("x")', 1, lambda x, y: x + 1, 'Binary(Plus(Int(32,Unknown)),Sym("x"),Lit(Int(32,Unknown),1))'),
		('Sym("x")', 1, lambda x, y: 1 << x, 'Binary(LShift(32),Lit(Int(32,Unknown),1),Sym("x"))'),
	]

	def testExpr(self):
		for lexpr, rexpr, func, expectedResultStr in self.exprTestCases:
			if lexpr is not None:
				if isinstance(lexpr, basestring):
					lexpr = self.factory.parse(lexpr)
					lexpr = ir.Expr(lexpr)
			if rexpr is not None:
				if isinstance(rexpr, basestring):
					rexpr = self.factory.parse(rexpr)
					rexpr = ir.Expr(rexpr)
			expectedResult = self.factory.parse(expectedResultStr)

			if rexpr is None:
				result = func(lexpr)
			else:
				result = func(lexpr, rexpr)
			result = result.term
			
			self.failUnlessEqual(result, expectedResult)
		


if __name__ == '__main__':
	unittest.main()