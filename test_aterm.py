#!/usr/bin/env python


import unittest

import aterm


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.Factory()

	def parseList(self, args, escape = '!'):
		result = []
		for arg in args:
			if isinstance(arg, basestring) and arg.startswith(escape):
				result.append(self.factory.parse(arg[len(escape):]))
			else:
				result.append(arg)	
		return result
	
	intTestCases = [
		'0',
		'1', 
		'-2', 
		'1234567890',
	]
	
	def testInt(self):
		for termStr in self.intTestCases:
			value = int(termStr)
			term = self.factory.parse(termStr)
			self.failUnless(term.factory is self.factory)
			self.failUnlessEqual(term.getType(), aterm.INT)
			self.failUnlessEqual(term.getValue(), value)

	realTestCases = [
		'12.345',
		'0.0', 
		'-2.1', 
		'0.1E10',
		'0.1E-10',
		'1.2',
	]
	
	def testReal(self):
		for termStr in self.realTestCases:
			value = float(termStr)
			term = self.factory.parse(termStr)
			self.failUnless(term.factory is self.factory)
			self.failUnlessEqual(term.getType(), aterm.REAL)
			self.failUnlessAlmostEqual(term.getValue(), value)

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
			term = self.factory.parse(termStr)
			self.failUnless(term.factory is self.factory)
			self.failUnlessEqual(term.getType(), aterm.STR)
			self.failUnlessEqual(term.getValue(), value)

	applTestCases = [
		('a', 'a', 0),
		('a{1,2}', 'a', 0),
		('a()', 'a', 0),
		('a(){1,2}', 'a', 0),
		('a(1)', 'a', 1),
		('a(1,2)', 'a', 2),
		('a(1,2){1,2}', 'a', 2),
	]
	
	def testAppl(self):
		for termStr, name, arity in self.applTestCases:
			term = self.factory.parse(termStr)
			self.failUnless(term.factory is self.factory)
			self.failUnlessEqual(term.getType(), aterm.APPL)
			self.failUnlessEqual(term.getName(), name)
			self.failUnlessEqual(term.getArity(), arity)
	
	listTestCases = [
		('[]', 0),
		('[]{1,2}', 0),
		('[1]', 1),
		('[1]{1,2}', 1),
		('[1,2]', 2),
		('[1,2]{1,2}', 2),
	]
	
	def testList(self):
		for termStr, length in self.listTestCases:
			term = self.factory.parse(termStr)
			self.failUnless(term.factory is self.factory)
			self.failUnlessEqual(term.getType(), aterm.LIST)
			self.failUnlessEqual(term.isEmpty(), length == 0)
			self.failUnlessEqual(term.getLength(), length)
	
	identityTestCases = [
		# ints
		['1', '2'],
		
		# reals
		['0.1', '0.2'],
		
		# strings
		[r'""', r'"a"', r'"a b"'],
		
		# applications
		['a', 'b', 'a(1)', 'a(1,2)'],
		
		# lists
		['[]', '[1]', '[1,2]'],

		# placeholders
		['<a>', '<b>'],
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

						if term1.getType() != aterm.PLACEHOLDER and term2.getType() != aterm.PLACEHOLDER: 
							result = term1.match(term2)
							self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))
						
						if expectedResult is True:
							aterm2 = term2.setAnnotations(annos)

							assert isinstance(term2, aterm.ATerm)
							
							result = term1.isEquivalent(aterm2)
							self.failUnlessEqual(result, True, msg = '%s <=> %s{...} = %r (!= %r)' % (term1Str, term2Str, result, True))						
	
							result = term1.isEqual(aterm2)
							self.failUnlessEqual(result, False, msg = '%s == %s{...} = %r (!= %r)' % (term1Str, term2Str, result, False))						
	
							if term1.getType() != aterm.PLACEHOLDER and term2.getType() != aterm.PLACEHOLDER:
								result = term1.match(aterm2)
								self.failUnlessEqual(result, True, msg = '%s ~ %s{...} = %r (!= %r)' % (term1Str, term2Str, result, True))

	matchTestCases = [
		# ints
		('1', '<int>', True, [1]),
		('1', '<term>', True, ['!1']),
		('1', '<real>', False, []),
		('1', '<str>', False, []),
		('1', '<appl>', False, []),
		('1', '<fun>', False, []),
		('1', '<list>', False, []),
		('1', '<placeholder>', False, []),

		# reals
		('0.1', '<real>', True, [0.1]),
		('0.1', '<term>', True, ['!0.1']),
		('0.1', '<int>', False, []),
		('0.1', '<appl>', False, []),
		('0.1', '<fun>', False, []),
		('0.1', '<list>', False, []),
		('0.1', '<placeholder>', False, []),
		
		# strings
		('"ab"', '<str>', True, ['ab']),
		('"ab"', '<term>', True, ['!"ab"']),
		('"ab"', '<int>', False, []),
		('"ab"', '<real>', False, []),
		('"ab"', '<appl>', False, []),
		('"ab"', '<fun>', False, []),
		('"ab"', '<list>', False, []),
		('"ab"', '<placeholder>', False, []),
		
		# lists
		('[]', '[<list>]', True, ['![]']),
		('[1]', '[<list>]', True, ['![1]']),
		('[1,2]', '[<list>]', True, ['![1,2]']),
		('[1,2]', '[1,<list>]', True, ['![2]']),
		('[1,2]', '[1,2,<list>]', True, ['![]']),
		('[1,2]', '<term>', True, ['![1,2]']),
		('[1,2]', '<int>', False, []),
		('[1,2]', '<real>', False, []),
		('[1,2]', '<str>', False, []),
		('[1,2]', '<appl>', False, []),
		('[1,2]', '<fun>', False, []),
		('[1,2]', '<placeholder>', False, []),
		('[1]', '[<int>]', True, [1]),
		('[1,0.2,"c"]', '[<int>,<real>,<str>]', True, [1, 0.2, 'c']),
		('[1,2,3]', '[<int>,<list>]', True, [1, '![2,3]']),

		# appls
		('a', '<appl>', True, ['!a']),
		('a', '<fun>', True, ['a']),
		('a(1)', '<appl>', True, ['!a(1)']),
		('a(1,2)', '<appl>', True, ['!a(1,2)']),
		('a(1,2)', '<term>', True, ['!a(1,2)']),
		('a(1,2)', '<int>', False, []),
		('a(1,2)', '<real>', False, []),
		('a(1,2)', '<str>', False, []),
		('a(1,2)', '<list>', False, []),
		('a(1,2)', '<placeholder>', False, []),
		('a(1)', 'a(<int>)', True, [1]),
		('a(1,2)', 'a(<int>,<int>)', True, [1, 2]),
		('a(1,2,3)', 'a(<int>,<list>)', True, [1, '![2,3]']),
		('a(1,2,3)', '<fun(<int>,<list>)>', True, ['a', 1, '![2,3]']),
		('a(1,2,3)', '<fun>', False, ['a']),

		# placeholders
		('<a>', '<placeholder>', True, ['!<a>']),
		('<a>', '<term>', True, ['!<a>']),
		('<a>', '<int>', False, []),
		('<a>', '<real>', False, []),
		('<a>', '<str>', False, []),
		('<a>', '<appl>', False, []),
		('<a>', '<fun>', False, []),
		('<a>', '<list>', False, []),

	]
	
	def testMatch(self):
		for termStr, patternStr, expectedResult, expectedMatchesStr in self.matchTestCases:
			
			term = self.factory.parse(termStr)
			pattern = self.factory.parse(patternStr)
			expectedMatches = self.parseList(expectedMatchesStr)
			
			matches = []
			result = term.match(pattern, matches)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, result, expectedResult))
			self.failUnlessEqual(matches, expectedMatches, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, matches, expectedMatches))

	makeTestCases = [
		('1', [], '1'),
		('0.1', [], '0.1'),
		('"a"', [], '"a"'),
		('[1,2]', [], '[1,2]'),
		('a(1,2)', [], 'a(1,2)'),
		
		('<int>', [1], '1'),
		('<real>', [0.1], '0.1'),
		('<str>', ['a'], '"a"'),
		('<appl>', ['a'], 'a'),
		('<appl(1,2)>', ['a'], 'a(1,2)'),
		('<appl(<int>,<real>)>', ['a', 1, 0.2], 'a(1,0.2)'),
		('<placeholder>', ['!a'], '<a>'),
		('<term>', ['!a'], 'a'),
		
		('a(1,<int>)', [2], 'a(1,2)'),
		('[1,2,<list>]', ['![3,4]'], '[1,2,3,4]'),
	]

	def testMake(self):
		for patternStr, argsStr, expectedResultStr in self.makeTestCases:
			args = self.parseList(argsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			result = self.factory.make(patternStr, *args)
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
