#!/usr/bin/env python


import unittest

import term


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = term.Factory()

	def parseVars(self, vars):
		res = {}
		for name, value in vars.iteritems():
			res[name] = self.factory.parse(value)
		return res
	
	intTestCases = [
		'0',
		'1', 
		'-2', 
		'1234567890',
	]
	
	def testInt(self):
		for termStr in self.intTestCases:
			value = int(termStr)
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), term.INT)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)

	realTestCases = [
		'0.0',
		'1.2',
		'1.', 
		'.1', 
		'-1.2', 
		'0.1E10',
		'0.1E-10',
		'0.1E+10',
		'1E10',
		'12345.67890',
	]
	
	def testReal(self):
		for termStr in self.realTestCases:
			value = float(termStr)
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), term.REAL)
			self.failUnlessAlmostEqual(_term.getValue(), value)

	strTestCases = [
		(r'""', ''),
		(r'" "', ' '),
		(r'"\""', "\""),
		(r'"\t"', '\t'),
		(r'"\r"', '\r'),
		(r'"\n"', '\n'),
	]
	
	def testStr(self):
		for termStr, value in self.strTestCases:
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), term.STR)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)

	listTestCases = [
		('[]', 0),
		('[1]', 1),
		('[1,2]', 2),
	]
	
	def testList(self):
		for termStr, length in self.listTestCases:
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), term.LIST)
			self.failUnlessEqual(_term.isEmpty(), length == 0)
			self.failUnlessEqual(_term.getLength(), length)
			self.failUnlessEqual(str(_term), termStr)
	
	applTestCases = [
		('C()', 'C', 0),
		('C(1)', 'C', 1),
		('C(1,2)', 'C', 2),
		('a()', 'a', 0),
		('a(1)', 'a', 1),
		('a(1,2)', 'a', 2),
		('_()', '_', 0),
		('_(1)', '_', 1),
		('_(1,2)', '_', 2),
	]
	
	def testCons(self):
		for termStr, name, arity in self.applTestCases:
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), term.APPL)
			self.failUnlessEqual(str(_term.getName()), name)
			self.failUnlessEqual(_term.getArity(), arity)
			self.failUnlessEqual(str(_term), termStr)
	
	identityTestCases = [
		# ints
		['1', '2'],
		
		# reals
		['0.1', '0.2'],
		
		# strings
		[r'""', r'"a"', r'"a b"'],
		
		# cons
		['A', 'B'],

		# vars
		['a', 'b'],

		# wildcard
		['_'],

		# lists
		['[]', '[1]', '[1,2]', '[1,*]'],

		# applications
		['A()', 'B()', 'A(1)', 'A(1,2)', 'A(1,*)'],
		['a()', 'b()', 'a(1)', 'a(1,2)', 'a(1,*)'],
		['_()', '_(1)', '_(1,2)', '_(1,*)'],
		
	]

	def testIdentity(self):
		annos = self.factory.parse('[1,2]')
		
		for terms1Str in self.identityTestCases:
			for terms2Str in self.identityTestCases:
				for term1Str in terms1Str:
					for term2Str in terms2Str:
						term1 = self.factory.parse(term1Str)
						term2 = self.factory.parse(term2Str)
			
						expectedResult = term1Str == term2Str
											
						result = term1.isEquivalent(term2)
						self.failUnlessEqual(result, expectedResult, msg = '%s <=> %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))						

						result = term1.isEqual(term2)
						self.failUnlessEqual(result, expectedResult, msg = '%s == %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))						

						if term1.isConstant():
							result = term1.match(term2)
							self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))
						
	def testWrite(self):
		for terms1Str in self.identityTestCases:
				for term1Str in terms1Str:
					term1 = self.factory.parse(term1Str)
					
					term2Str = str(term1)
			
					self.failUnlessEqual(term1Str, term2Str)
						
	matchTestCases = [
		# ints
		('1', 'a', True, {'a':'1'}),
		('1', '_', True, {}),

		# reals
		('0.1', 'a', True, {'a':'0.1'}),
		('0.1', '_', True, {}),
		
		# strings
		('"a"', 'a', True, {'a':'"a"'}),
		('"a"', '_', True, {}),
		
		# lists
		('[]', '[*]', True, {}),
		('[]', '[*a]', True, {'a':'[]'}),
		('[1]', '[*]', True, {}),
		('[1]', '[*a]', True, {'a':'[1]'}),
		('[1,2]', '[*]', True, {}),
		('[1,2]', '[*a]', True, {'a':'[1,2]'}),
		('[1,2]', '[1,*]', True, {}),
		('[1,2]', '[1,*a]', True, {'a':'[2]'}),
		('[1,2]', '[1,2,*]', True, {}),
		('[1,2]', '[1,2,*a]', True, {'a':'[]'}),
		('[1,2]', 'a', True, {'a':'[1,2]'}),
		('[1,0.2,"c"]', '[a,b,c]', True, {'a':'1', 'b':'0.2', 'c':'"c"'}),
		('[1,2,3]', '[a,*b]', True, {'a':'1', 'b':'[2,3]'}),
		('[1,2,1,2]', '[a,b,a,b]', True, {'a':'1', 'b':'2'}),

		# appls
		('C()', 'a', True, {'a':'C()'}),
		('C(1)', 'a', True, {'a':'C(1)'}),
		('C(1,2)', 'a', True, {'a':'C(1,2)'}),
		('C(1)', 'C(a)', True, {'a':'1'}),
		('C(1,2)', 'C(a,b)', True, {'a':'1', 'b':'2'}),
		('C(1,2,3)', 'C(*a)', True, {'a':'[1, 2,3]'}),
		('C(1,2,3)', 'C(a,*b)', True, {'a':'1', 'b':'[2,3]'}),
		('C(1,2,3)', 'a(b,*c)', True, {'a':'C', 'b':'1', 'c':'[2,3]'}),
		('C(1,2,3)', 'a()', False, {'a':'C'}),
	]
	
	def testMatch(self):
		for termStr, patternStr, expectedResult, expectedVarsStr in self.matchTestCases:
			
			term = self.factory.parse(termStr)
			pattern = self.factory.parse(patternStr)
			expectedVars = self.parseVars(expectedVarsStr)
			
			vars = {}
			result = pattern.match(term, vars)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, result, expectedResult))
			self.failUnlessEqual(vars, expectedVars, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, vars, expectedVars))

	makeTestCases = [
		('1', {}, '1'),
		('0.1', {}, '0.1'),
		('"a"', {}, '"a"'),
		('[1,2]', {}, '[1,2]'),
		('C(1,2)', {}, 'C(1,2)'),
		
		('a', {'a':'1'}, '1'),
		('a', {'a':'0.1'}, '0.1'),
		('a', {'a':'"a"'}, '"a"'),
		('a', {'a':'a'}, 'a'),
		('a(1,2)', {'a':'C'}, 'C(1,2)'),
		('a(b,c)', {'a':'C', 'b':'1', 'c':'0.2'}, 'C(1,0.2)'),
		('a', {'a':'C'}, 'C'),
		
		('C(1,b)', {'b':'2'}, 'C(1,2)'),
		('[1,2,*a]', {'a':'[3,4]'}, '[1,2,3,4]'),
	]

	def testMake(self):
		for patternStr, varsStr, expectedResultStr in self.makeTestCases:
			vars = self.parseVars(varsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			result = self.factory.make(patternStr, vars)
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
