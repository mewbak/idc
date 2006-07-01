#!/usr/bin/env python
'''Unit tests for the aterm package.'''


import unittest

import aterm.factory
import aterm.types


class TestTerm(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.factory.factory

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
	
	def failIfMutable(self, obj):
		# XXX: disabled
		return
		for name in dir(obj):
			try:
				setattr(obj, name, None)
			except AttributeError:
				pass
			else:
				self.fail('attribute "%s" is modifiable' % name)
				
			try:
				delattr(obj, name)
			except AttributeError:
				pass
			except TypeError:
				pass
			else:
				self.fail('attribute "%s" is deletable' % name)


	def testInt(self):
		for termStr in self.intTestCases:
			value = int(termStr)
			_term = self.factory.parse(termStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), aterm.types.INT)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

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
			self.failUnlessEqual(_term.getType(), aterm.types.REAL)
			self.failUnlessAlmostEqual(_term.getValue(), value)
			self.failIfMutable(_term)

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
			self.failUnlessEqual(_term.getType(), aterm.types.STR)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

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
			self.failUnless(_term.getType() & aterm.types.LIST)
			self.failUnlessEqual(_term.isEmpty(), length == 0)
			self.failUnlessEqual(_term.getLength(), length)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)
	
	applTestCases = [
		('C', '"C"', 0),
		('C(1)', '"C"', 1),
		('C(1,2)', '"C"', 2),
	]
	
	def testAppl(self):
		for termStr, nameStr, arity in self.applTestCases:
			_term = self.factory.parse(termStr)
			name = self.factory.parse(nameStr)
			self.failUnless(_term.factory is self.factory)
			self.failUnlessEqual(_term.getType(), aterm.types.APPL)
			self.failUnlessEqual(_term.getName(), name)
			self.failUnlessEqual(_term.getArity(), arity)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)
	
	identityTestCases = [
		# ints
		['1', '2'],
		
		# reals
		['0.1', '0.2'],
		
		# strings
		['""', '"s"', '"st"'],
		
		# lists
		['[]', '[1]', '[1,2]'],

		# applications
		['()', '(1)', '(1,2)'],
		['C', 'D', 'C(1)', 'C(1,2)'],
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

						if expectedResult:
							term2 = term2.setAnnotation("A", self.factory.parse("1"))
							
							result = term1.isEquivalent(term2)
							self.failUnlessEqual(result, True, msg = '%s <=> %s = %r (!= %r)' % (term1Str, term2Str, result, True))
	
							result = term1.isEqual(term2)
							self.failUnlessEqual(result, False, msg = '%s == %s = %r (!= %r)' % (term1Str, term2Str, result, False))
							
						
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
		('C(1,2,3)', '_(_,*)', True, ['"C"', '1', '[2,3]'], {}),
		('C(1,2,3)', 'f(x,*y)', True, [], {'f':'"C"', 'x':'1', 'y':'[2,3]'}),
		('C(1,2,3)', '_()', False, ['"C"'], {}),
		('C(1,2,3)', 'f()', False, [], {'f':'"C"'}),

		# tuples
		('(1,2,3)', '_(_,*)', True, ['""', '1', '[2,3]'], {}),
		('(1,2,3)', 'f(x,*y)', True, [], {'f':'""', 'x':'1', 'y':'[2,3]'}),
		
		# assigns
		('C(1,2)', 't=_(_,_)', True, [], {'t':'C(1,2)'}),
		('C(1,2)', 't=f(x,y)', True, [], {'t':'C(1,2)', 'f':'"C"', 'x':'1', 'y':'2'}),
	]
	
	def testMatch(self):
		for termStr, patternStr, expectedResult, expectedArgsStr, expectedKargsStr in self.matchTestCases:
			
			term = self.factory.parse(termStr)
			expectedArgs = self.parseArgs(expectedArgsStr)
			expectedKargs = self.parseKargs(expectedKargsStr)
			
			match = self.factory.match(patternStr, term)
			result = bool(match)
			
			self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, result, expectedResult))
			if match:
				self.failUnlessEqual(match.args, expectedArgs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, match.args, expectedArgs))
				self.failUnlessEqual(match.kargs, expectedKargs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, match.kargs, expectedKargs))

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
		('_()', ['"C"'], {}, 'C()'),
		('_(_,_)', ['"C"', '1', '2'], {}, 'C(1,2)'),
		('_(_,*)', ['"C"', '1', '[2]'], {}, 'C(1,2)'),
		
		# variable substitution in applications
		('C(x)', [], {'x':'1'}, 'C(1)'),
		('C(x,y)', [], {'x':'1', 'y':'2'}, 'C(1,2)'),
		('f()', [], {'f':'"C"'}, 'C()'),
		('f(x,y)', [], {'f':'"C"', 'x':'1', 'y':'2'}, 'C(1,2)'),
		('f(x,*y)', [], {'f':'"C"', 'x':'1', 'y':'[2]'}, 'C(1,2)'),
	]

	def testMake(self):
		for patternStr, argsStr, kargsStr, expectedResultStr in self.makeTestCases:
			args = self.parseArgs(argsStr)
			kargs = self.parseKargs(kargsStr)
			expectedResult = self.factory.parse(expectedResultStr)
			result = self.factory.make(patternStr, *args, **kargs)
			self.failUnlessEqual(result, expectedResult)

	def _testHash(self, cmpf, hashf, msg = None):
		for terms1Str in self.identityTestCases:
			for term1Str in terms1Str:
				term1 = self.factory.parse(term1Str)
				hash1 = hashf(term1)
				self.failUnless(isinstance(hash1, int))
				self.failIfEqual(hash1, -1)
				for terms2Str in self.identityTestCases:
					for term2Str in terms2Str:
						term2 = self.factory.parse(term2Str)
						hash2 = hashf(term2)
						term_eq = cmpf(term1, term2)
						hash_eq = hash1 == hash2
						detail = '%s (0x%08x) and %s (0x%08x)' % (
							term1Str, hash1, term2Str, hash2
						)
						if term_eq:
							self.failUnless(hash_eq,
								'%s hash/equality incoerence for '
								'%s' % (msg, detail)
							)
						elif 0: 
							# XXX: this fails on python 2.3 but no on 2.4...
							self.failIf(hash_eq,
								'%s hash colision for '
								'%s' % (msg, detail)
							)

	def testHash(self):
		self._testHash(
			lambda t, o: t.isEquivalent(o), 
			lambda t: t.getStructuralHash(), 
			msg = 'structural'
		)
		self._testHash(
			lambda t, o: t.isEqual(o), 
			lambda t: t.getHash(), 
			msg = 'full'
		)
		self._testHash(
			lambda t, o: t == o, 
			lambda t: hash(t), 
			msg = 'python'
		)
		
	def testAnnotations(self):
		factory = self.factory
	
		for terms1Str in self.identityTestCases:
			for term1Str in terms1Str:
				term1 = self.factory.parse(term1Str)
				
				term = term1
				self.failUnlessEqual(term.getAnnotations(), factory.parse("[]"))
				
				term = term.setAnnotation("A(_)", factory.parse("A(1)"))
				self.failUnlessEqual(term.getAnnotations(), factory.parse("[A(1)]"))
				
				term = term.setAnnotation("B(_)", factory.parse("B(2)"))
				self.failUnlessEqual(term.getAnnotation("A(_)"), factory.parse("A(1)"))
				self.failUnlessEqual(term.getAnnotation("B(_)"), factory.parse("B(2)"))
		
				term = term.setAnnotation("A(_)", factory.parse("A(3)"))
				self.failUnlessEqual(term.getAnnotation("A(_)"), factory.parse("A(3)"))
				self.failUnlessEqual(term.getAnnotation("B(_)"), factory.parse("B(2)"))
		
				try:
					term.getAnnotation("C(_)")
					self.fail()
				except ValueError:
					pass
		
				self.failUnless(term.isEquivalent(term1))


if __name__ == '__main__':
	unittest.main()
