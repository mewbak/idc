#!/usr/bin/env python


import os
import unittest

import refactoring


def main():
	# TODO: rewrite this as a TestLoader
	suite = unittest.TestSuite()
	for name in os.listdir(refactoring.__path__[0]):
		if name.endswith('.py') and not name.startswith('_'):
			suite.addTest(unittest.defaultTestLoader.loadTestsFromName('refactoring.' + name[:-3]))
	factory = refactoring.Factory()
	for r in factory.refactorings.itervalues():
		suite.addTests(r.getTests())
	unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
	main()
