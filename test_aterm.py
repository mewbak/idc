#!/usr/bin/env python


import unittest

import aterm


class TestCase(unittest.TestCase):
	
	def setUp(self):
		self.f = aterm.ATermFactory()

	def testMakeInt(self):
		for v in [-2, 0, 1]:
			t = self.f.makeInt(v)
			self.failUnless(t.factory is self.f)
			self.failUnlessEqual(t.type, aterm.INT)
			self.failUnlessEqual(t.value, v)
			self.failUnlessEqual(str(t), str(v))
	
	def testMakeReal(self):
		for v in [-2.1, 0.0, 1.2]:
			t = self.f.makeReal(v)
			self.failUnless(t.factory is self.f)
			self.failUnlessEqual(t.type, aterm.REAL)
			self.failUnlessEqual(t.value, v)
			self.failUnlessEqual(float(str(t)), v)

	def testParseInt(self):
		for s in ["-2", "0", "1", "123456789"]:
			t = self.f.parse(s)
			self.failUnlessEqual(t.type, aterm.INT)
			self.failUnlessEqual(t.value, int(s))
		
	def testParseReal(self):
		for s in ["0.0", "1.0", "23.3", "-4.5", "6.7E8", "9.0E-12"]:
			t = self.f.parse(s)
			self.failUnlessEqual(t.type, aterm.REAL)
			self.failUnlessEqual(t.value, float(s))

	def testParseAppl(self):
		t = self.f.parse("asdf")
		self.failUnlessEqual(t.type, aterm.APPL)
		self.failUnlessEqual(t.afun, "asdf")
		self.failUnlessEqual(t.getArity(), 0)

		t = self.f.parse("asdf(1,2)")
		self.failUnlessEqual(t.type, aterm.APPL)
		self.failUnlessEqual(t.afun, "asdf")
		self.failUnlessEqual(t.getArity(), 2)
		

if __name__ == '__main__':
	unittest.main()
