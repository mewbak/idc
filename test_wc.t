header {
import unittest

import aterm
import walker
}

class Simple:

	swap
		: C(x,y) -> C(y,x)
		| _
		;


header {

class TestCase(unittest.TestCase):

	def setUp(self):
		self.factory = aterm.Factory()
		self.transformation = Simple(self.factory)
	
	swapTestCases = [
		("C(1,2)", "C(2,1)"),
		("C(1,2,3)", "C(1,2,3)"),
		("D", "D"),
	]
	
	def testSwap(self):
		for inputStr, expectedResultStr in self.swapTestCases:
			input = self.factory.parse(inputStr)
			expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = self.transformation.swap(input)
			except walker.TransformationFailureExcpetion:
				result = None
		
			self.failUnlessEqual(result, expectedResult, msg = '%r -> %r (!= %r)' % (input, result, expectedResult))						

}

header {

if __name__ == '__main__':
	unittest.main()

}
