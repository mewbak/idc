"""Unit-tests for walker generator."""

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
		| (1)
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
		('(1)', '(1)'),
		('(1,2)', Failure),
		('(1,2)', Failure),
		('C(1)', 'C(1)'),
		('D(1,2)', Failure),
	]
	}

	testBuild
		: 1 -> 2
		| 0.1 -> 0.2
		| "s" -> "t"
		| [1] -> [2,3]
		| (1) -> (2,3)
		| C(1) -> D(2,3)
		;
	
	{
	testBuildData = [
		('1', '2'),
		('0.1', '0.2'),
		('"s"', '"t"'),
		('[1]', '[2,3]'),
		('(1)', '(2,3)'),
		('C(1)', 'D(2,3)'),
	]
	}
	
	testVariables
		: First(x,_) -> x
		| Second(_,x) -> x
		| Equal(x,x) -> x
		| Head(x,*) -> x
		| Tail(_,*x) -> x
		;
		
	{
	testVariablesData = [
		('First(1,2)', '1'),
		('First(1)', Failure),
		('First()', Failure),
		('Second(1,2,3)', Failure),
		('Second(1,2)', '2'),
		('Second(1)', Failure),
		('Equal(1,1)', '1'),
		('Equal(1,2)', Failure),
		('Equal(1)', Failure),
		('Head(1,2,3)', '1'),
		('Head(1,2)', '1'),
		('Head(1)', '1'),
		('Head()', Failure),
		('Tail(1,2,3)', '[2,3]'),
		('Tail(1,2)', '[2]'),
		('Tail(1)', '[]'),
		('Tail()', Failure),
	]
	}

	testConstructors
		: f(*a) -> Appl(f, a)
		;
	
	{
	testConstructorsData = [
		('()', 'Appl("",[])'),
		('(1)', 'Appl("",[1])'),
		('(1,2)', 'Appl("",[1,2])'),
		('C', 'Appl("C",[])'),
		('C(1)', 'Appl("C",[1])'),
		('C(1,2)', 'Appl("C",[1,2])'),
		('1', Failure),
		('0.1', Failure),
		('"s"', Failure),
		('[1]', Failure),
	]
	}

	testPredicateAction
		: x 
			{ $x.getType() == aterm.INT and $x.getValue() > 0 }?
		;
	
	{
	testPredicateActionData = [
		('1', '1'),
		('0', Failure),
		('-1', Failure),
		('0.1', Failure),
		('"s"', Failure),
		('[1]', Failure),
		('(1)', Failure),
		('C(1,2)', Failure),
	]
	}

	testProductionAction
		: Plus(x,y)
			{ $$ = self.factory.makeInt($x.getValue() + $y.getValue()) }
		;
	
	{
	testProductionActionData = [
		('Plus(1,2)', '3'),
	]
	}

	isZero
		"""Matches zero"""
		: 0
		;

	testPredicateMethod
		: Int(_isZero) -> Null
		| Int(_)
		;

	{
	testPredicateMethodData = [
		('Int(0)', 'Null'),
		('Int(1)', 'Int(1)'),
	]
	}
	
	invert
		: True -> False
		| False -> True
		;

	testProductionMethod
		: x -> _invert(x)
		;

	{
	testProductionMethodData = [
		('True', 'False'),
		('False', 'True'),
	]
	}
	
	testMethodArg(x, {y})
		: 1 -> x
		| 2 { $$ = y }
		;
	
	{
	testMethodArgData = [
		('1', '"x"', '"y"', '"x"'),
		('2', '"x"', '"y"', '"y"'),
	]
	}
	


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
		
		for testDataItem in testData:
			inputStr = testDataItem[0]
			argsStr = testDataItem[1:-1]
			expectedResultStr = testDataItem[-1]
			
			input = self.factory.parse(inputStr)

			args = [self.factory.parse(argStr) for argStr in argsStr]

			if expectedResultStr is Failure:
				expectedResult = failure
			else:
				expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = testMethod(input, *args)
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
