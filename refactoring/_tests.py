#!/usr/bin/env python


import os
import unittest
import traceback

import aterm.factory
import transf.transformation
import refactoring


class TransformationTest(unittest.TestCase):
	'''A test case based on a transformation.'''

	def __init__(self, transf, transfName = None):
		unittest.TestCase.__init__(self)
		self.__transf = transf
		self.__transfName = transfName

	def runTest(self):
		#try:
			self.__transf(aterm.factory.factory.makeStr("Ignored"))
		#except transf.exception.Failure, ex:
		#	self.fail(msg = str(ex))

	def shortDescription(self):
		return self.__transfName


def main():
	# TODO: rewrite this as a TestLoader
	suite = unittest.TestSuite()
	for name in os.listdir(refactoring.__path__[0]):
		name, ext = os.path.splitext(name)
		if name != '__init__' and ext == '.py':
			try:
				module = __import__('refactoring.' + name)
			except:
				traceback.print_exc()
			else:
				module = getattr(module, name)
				for nam in dir(module):
					if nam.startswith('test'):
						obj = getattr(module, nam)
						if isinstance(obj, transf.transformation.Transformation):
							test = TransformationTest(obj, module.__name__ + '.' + nam)
							suite.addTest(test)
	unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
	main()
