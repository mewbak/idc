#!/usr/bin/env python


import sys

import aterm.factory 
from ir import PrettyPrinter
import box
import path
from machine.pentium import Pentium


def pretty_print(term):
	printer = PrettyPrinter(term.factory)
	boxes = printer.module(term)
	print box.box2text(boxes, box.AnsiTextFormatter)


def translate(filename):
	print '* %s *' % filename
	print
	
	factory = aterm.factory.Factory()
	machine = Pentium()
	
	print '** Assembly **'	
	print file(filename, 'rt').read()
	print
	
	print '** Low-level IR **'	
	term = machine.load(factory, file(filename, 'rt'))
	pretty_print(term)
	print
	
	print '** Translated IR **'	
	term = machine.translate(term)
	term = path.annotate(term)
	pretty_print(term)
	print

	print


def main():
	for arg in sys.argv[1:]:
		translate(arg)


if __name__ == '__main__':
	import hotshot
	filename = "pythongrind.prof"
	prof = hotshot.Profile(filename, lineevents=0)
	prof.runcall(main)
	prof.close()

	#main()

