header {
import unittest

import aterm
import walker
}

class Simple:

	match
		: 1
		| 0.1
		| "s"
		| [1]
		| C(1)
		;
	
	build
		: 1 -> 2
		| 0.1 -> 0.2
		| "s" -> "t"
		| [1] -> [2,3]
		| C(1) -> D(2,3)
		;
	
	variables
		: First(x,y) -> x
		| Second(x,y) -> y
		| Equal(x,x) -> x
		| Tail(x,*y) -> y
		| f(*a) -> Cons(f, a)
		;
		
	swap
		: C(x,y) -> C(y,x)
		| _
		;

	is_zero
		: 0
		;

	simplify
		: Or(.is_zero,x) -> x
		;

header {

class TestCase(unittest.TestCase):

	def setUp(self):
		self.factory = aterm.Factory()
		self.transformation = Simple(self.factory)

	def runTestCases(self, method, testcases):
		failure = self.factory.parse("FAILURE")
		for inputStr, expectedResultStr in testcases:
			input = self.factory.parse(inputStr)

			if expectedResultStr is None:
				expectedResult = failure
			else:
				expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = getattr(self.transformation, method)(input)
			except walker.TransformationFailureException:
				result = failure
		
			self.failUnlessEqual(result, expectedResult, msg = '%r -> %r (!= %r)' % (input, result, expectedResult))						
	
	matchTestCases = [
		('1', '1'),
		('2', None),
		('0.1', '0.1'),
		('0.2', None),
		('"s"', '"s"'),
		('"t"', None),
		('[1]', '[1]'),
		('[1,2]', None),
		('[1,2]', None),
		('C(1)', 'C(1)'),
		('D(1,2)', None),
	]
	
	def testMatch(self):
		self.runTestCases("match", self.matchTestCases)

	buildTestCases = [
		('1', '2'),
		('0.1', '0.2'),
		('"s"', '"t"'),
		('[1]', '[2,3]'),
		('C(1)', 'D(2,3)'),
	]
	
	def testBuild(self):
		self.runTestCases("build", self.buildTestCases)

	variablesTestCases = [
		('First(1,2)', '1'),
		('Second(1,2)', '2'),
		('Equal(1,1)', '1'),
		('Equal(1,2)', 'Cons("Equal",[1,2])'),
	]
	
	def testVariables(self):
		self.runTestCases("variables", self.variablesTestCases)

	swapTestCases = [
		("C(1,2)", "C(2,1)"),
		("C(1,2,3)", "C(1,2,3)"),
		("D", "D"),
	]
	
	def testSwap(self):
		self.runTestCases("swap", self.swapTestCases)

}

header {

if __name__ == '__main__':
	unittest.main()

}
