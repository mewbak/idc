#!/usr/bin/env python


import unittest

import aterm


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
			self.failUnlessEqual(_term.getType(), aterm.INT)
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
			self.failUnlessEqual(_term.getType(), aterm.REAL)
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
			self.failUnlessEqual(_term.getType(), aterm.STR)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)

	listTestCases = [
		('[]', 0),
		('[1]', 1),
		('[1,2]', 2),
		('[[],[1],[1,[2]]]', 3),
	]
	
	def testList(self):
		for termStr, length in self.listTestCases:
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), aterm.LIST)
			self.failUnlessEqual(_term.isEmpty(), length == 0)
			self.failUnlessEqual(_term.getLength(), length)
			self.failUnlessEqual(str(_term), termStr)
	
	applTestCases = [
		('C', 'C', 0),
		('C(1)', 'C', 1),
		('C(1,2)', 'C', 2),
		('f()', 'f', 0),
		('f(x)', 'f', 1),
		('f(x,y)', 'f', 2),
		('_()', '_', 0),
		('_(_)', '_', 1),
		('_(_,_)', '_', 2),
	]
	
	def testAppl(self):
		for termStr, symbol, arity in self.applTestCases:
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), aterm.APPL)
			self.failUnlessEqual(_term.getName().getSymbol(), symbol)
			self.failUnlessEqual(_term.getArity(), arity)
			self.failUnlessEqual(str(_term), termStr)
	
	identityTestCases = [
		# ints
		['1', '2'],
		
		# reals
		['0.1', '0.2'],
		
		# strings
		['""', '"s"', '"st"'],
		
		# vars
		['x', 'y'],

		# wildcard
		['_'],

		# lists
		['[]', '[1]', '[1,2]', '[1,*]'],

		# applications
		['C', 'D', 'C(1)', 'C(1,2)', 'C(1,*)'],
		['f()', 'g()', 'f(x)', 'f(x,y)', 'f(x,*y)'],
		['_()', '_(_)', '_(_,_)', '_(_,*)'],
		
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
		('1', '_', True, ['1'], {}),
		('1', 'x', True, [], {'x':'1'}),

		# reals
		('0.1', '_', True, ['0.1'], {}),
		('0.1', 'x', True, [], {'x':'0.1'}),
		
		# strings
		('"s"', '_', True, ['"s"'], {}),
		('"s"', 'x', True, [], {'x':'"s"'}),
		
		# lists
		('[]', '[*]', True, ['[]'], {}),
		('[]', '[*x]', True, [], {'x':'[]'}),
		('[1]', '[*]', True, ['[1]'], {}),
		('[1]', '[*x]', True, [], {'x':'[1]'}),
		('[1,2]', '[*]', True, ['[1,2]'], {}),
		('[1,2]', '[*x]', True, [], {'x':'[1,2]'}),
		('[1,2]', '[1,*]', True, ['[2]'], {}),
		('[1,2]', '[1,*x]', True, [], {'x':'[2]'}),
		('[1,2]', '[1,2,*]', True, ['[]'], {}),
		('[1,2]', '[1,2,*x]', True, [], {'x':'[]'}),
		('[1,2]', 'x', True, [], {'x':'[1,2]'}),
		('[1,0.2,"s"]', '[_,_,_]', True, ['1', '0.2', '"s"'], {}),
		('[1,0.2,"s"]', '[x,y,z]', True, [], {'x':'1', 'y':'0.2', 'z':'"s"'}),
		('[1,2,3]', '[_,*]', True, ['1', '[2,3]'], {}),
		('[1,2,3]', '[x,*y]', True, [], {'x':'1', 'y':'[2,3]'}),
		('[1,2,1,2]', '[x,y,x,y]', True, [], {'x':'1', 'y':'2'}),

		# appls
		('C', '_', True, ['C()'], {}),
		('C', 'x', True, [], {'x':'C()'}),
		('C()', '_', True, ['C'], {}),
		('C()', 'x', True, [], {'x':'C'}),
		('C(1)', '_', True, ['C(1)'], {}),
		('C(1)', 'x', True, [], {'x':'C(1)'}),
		('C(1,2)', '_', True, ['C(1,2)'], {}),
		('C(1,2)', 'x', True, [], {'x':'C(1,2)'}),
		('C(1)', 'C(_)', True, ['1'], {}),
		('C(1)', 'C(x)', True, [], {'x':'1'}),
		('C(1,2)', 'C(_,_)', True, ['1', '2'], {}),
		('C(1,2)', 'C(x,y)', True, [], {'x':'1', 'y':'2'}),
		('C(1,2,3)', 'C(*)', True, ['[1, 2,3]'], {}),
		('C(1,2,3)', 'C(*x)', True, [], {'x':'[1, 2,3]'}),
		('C(1,2,3)', 'C(_,*)', True, ['1', '[2,3]'], {}),
		('C(1,2,3)', 'C(x,*y)', True, [], {'x':'1', 'y':'[2,3]'}),
		('C(1,2,3)', '_(_,*)', True, ['"C"', '1', '[2,3]'], {}),
		('C(1,2,3)', 'f(x,*y)', True, [], {'f':'"C"', 'x':'1', 'y':'[2,3]'}),
		('C(1,2,3)', '_()', False, ['"C"'], {}),
		('C(1,2,3)', 'f()', False, [], {'f':'"C"'}),
		
	]
	
	def testMatch(self):
		for termStr, patternStr, expectedResult, expectedArgsStr, expectedKargsStr in self.matchTestCases:
			
			term = self.factory.parse(termStr)
			pattern = self.factory.parse(patternStr)
			expectedArgs = self.parseArgs(expectedArgsStr)
			expectedKargs = self.parseKargs(expectedKargsStr)
			
			args = []
			kargs = {}
			result = pattern.match(term, args, kargs)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, result, expectedResult))
			self.failUnlessEqual(args, expectedArgs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, args, expectedArgs))
			self.failUnlessEqual(kargs, expectedKargs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, kargs, expectedKargs))

	makeTestCases = [
		# constants terms
		('1', [], {}, '1'),
		('0.1', [], {}, '0.1'),
		('"s"', [], {}, '"s"'),
		('C', [], {}, 'C'),
		('[1,2]', [], {}, '[1,2]'),
		('C(1,2)', [], {}, 'C(1,2)'),
		
		# simple wildcard substitution
		('_', ['1'], {}, '1'),
		('_', ['0.1'], {}, '0.1'),
		('_', ['"s"'], {}, '"s"'),
		('_', ['C'], {}, 'C'),
		('_', ['[1,2]'], {}, '[1,2]'),
		('_', ['C(1,2)'], {}, 'C(1,2)'),
		
		# simple variable substitution
		('x', [], {'x':'1'}, '1'),
		('x', [], {'x':'0.1'}, '0.1'),
		('x', [], {'x':'"s"'}, '"s"'),
		('x', [], {'x':'C'}, 'C'),
		('x', [], {'x':'[1,2]'}, '[1,2]'),
		('x', [], {'x':'C(1,2)'}, 'C(1,2)'),
		
		# wildcard substitution in lists
		('[_]', ['1'], {}, '[1]'),
		('[_,_]', ['1', '2'], {}, '[1,2]'),
		('[*]', ['[1,2]'], {}, '[1,2]'),
		('[_,*]', ['1', '[2]'], {}, '[1,2]'),
		
		# variable substitution in lists
		('[x]', [], {'x':'1'}, '[1]'),
		('[x,y]', [], {'x':'1', 'y':'2'}, '[1,2]'),
		('[*x]', [], {'x':'[1,2]'}, '[1,2]'),
		('[x,*y]', [], {'x':'1', 'y':'[2]'}, '[1,2]'),
		
		# wildcard substitution in applications
		('C(_)', ['1'], {}, 'C(1)'),
		('C(_,_)', ['1', '2'], {}, 'C(1,2)'),
		('C(_,*)', ['1', '[2]'], {}, 'C(1,2)'),
		('_()', ['"C"'], {}, 'C()'),
		('_(_,_)', ['"C"', '1', '2'], {}, 'C(1,2)'),
		
		# variable substitution in applications
		('C(x)', [], {'x':'1'}, 'C(1)'),
		('C(x,y)', [], {'x':'1', 'y':'2'}, 'C(1,2)'),
		('C(x,*y)', [], {'x':'1', 'y':'[2]'}, 'C(1,2)'),
		('f()', [], {'f':'"C"'}, 'C()'),
		('f(x,y)', [], {'f':'"C"', 'x':'1', 'y':'2'}, 'C(1,2)'),
	]

	def testMake(self):
		for patternStr, argsStr, kargsStr, expectedResultStr in self.makeTestCases:
			args = self.parseArgs(argsStr)
			kargs = self.parseKargs(kargsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			result = self.factory.make(patternStr, *args, **kargs)
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
