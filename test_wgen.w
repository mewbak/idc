header {
import unittest

import aterm
import walker
}


class WalkerTestSuite:

	testMatch
		: 1
		| 0.1
		| "s"
		| [1]
		| C(1)
		;
	
	{
	testMatchData = [
		('1', '1'),
		('2', Failure),
		('0.1', '0.1'),
		('0.2', Failure),
		('"s"', '"s"'),
		('"t"', Failure),
		('[1]', '[1]'),
		('[1,2]', Failure),
		('[1,2]', Failure),
		('C(1)', 'C(1)'),
		('D(1,2)', Failure),
	]
	}

	testBuild
		: 1 -> 2
		| 0.1 -> 0.2
		| "s" -> "t"
		| [1] -> [2,3]
		| C(1) -> D(2,3)
		;
	
	{
	testBuildData = [
		('1', '2'),
		('0.1', '0.2'),
		('"s"', '"t"'),
		('[1]', '[2,3]'),
		('C(1)', 'D(2,3)'),
	]
	}
	
	testVariables
		: First(x,y) -> x
		| Second(x,y) -> y
		| Equal(x,x) -> x
		| Tail(x,*y) -> y
		| f(*a) -> Cons(f, a)
		;
		
	{
	testVariablesData = [
		('First(1,2)', '1'),
		('Second(1,2)', '2'),
		('Equal(1,1)', '1'),
		('Equal(1,2)', 'Cons("Equal",[1,2])'),
	]
	}
	
	testSwap
		: C(x,y) -> C(y,x)
		| _
		;

	{
	testSwapData = [
		("C(1,2)", "C(2,1)"),
		("C(1,2,3)", "C(1,2,3)"),
		("D", "D"),
	]
	}
	is_zero
		: 0
		;

	simplify
		: Or(.is_zero,x) -> x
		;


header {

class WalkerTestCase(unittest.TestCase):

	def __init__(self, walkerClass, testMethodName, testDataName):
		unittest.TestCase.__init__(self)

		self.walkerClass = walkerClass
		self.testMethodName = testMethodName
		self.testDataName = testDataName
	
	def setUp(self):
		self.factory = aterm.Factory()
		self.walker = self.walkerClass(self.factory)

	def runTest(self):
	
		failure = self.factory.parse("FAILURE")

		testMethod = getattr(self.walker, self.testMethodName)
		testData = getattr(self.walker, self.testDataName)
		
		for inputStr, expectedResultStr in testData:
			input = self.factory.parse(inputStr)

			if expectedResultStr is Failure:
				expectedResult = failure
			else:
				expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = testMethod(input)
			except walker.Failure, ex:
				result = failure
		
			self.failUnlessEqual(result, expectedResult, msg = '%r -> %r (!= %r)' % (input, result, expectedResult))						

	def id(self):
		return self.testMethodName

	def __str__(self):
		return "%s (%s)" % (self.walkerClass.__name__, self.testMethodName)
}

header {

def main():
	suite = unittest.TestSuite()
	walkerClass = WalkerTestSuite
	for attr in dir(walkerClass):
		if attr.startswith('test') and hasattr(walkerClass, attr + 'Data'):
			suite.addTest(WalkerTestCase(walkerClass, attr, attr + 'Data'))
	
	runner = unittest.TextTestRunner(verbosity = 2)
	runner.run(suite)


if __name__ == '__main__':
	main()

}
