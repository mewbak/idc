#!/usr/bin/env python


import sys
import optparse
import os
import os.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..')))

import aterm.factory 
import box
import ir
import machine.pentium


factory = aterm.factory.Factory()


def pretty_print(term):
	printer = ir.PrettyPrinter(term.factory)
	boxes = printer.module(term)
	sys.stderr.write(box.box2text(boxes, box.AnsiTextFormatter))


def translate(fpin, fpout, verbose = True):
	if verbose:
		sys.stderr.write('* %s *\n' % fpin.name)
		sys.stderr.write('\n')
	
	if verbose:
		sys.stderr.write('** Assembly **\n')	
		sys.stderr.write(fpin.read())
		sys.stderr.write('\n')	
		fpin.seek(0)
	
	mach = machine.pentium.Pentium()
	
	if verbose:
		sys.stderr.write('** Low-level IR **\n')	
		term = mach.load(factory, fpin)
		pretty_print(term)
		sys.stderr.write('\n')	
	
	term = mach.translate(term)

	if verbose:
		sys.stderr.write('** Translated IR **\n')
		pretty_print(term)
		sys.stderr.write('\n')	

		sys.stderr.write('\n')	

	term.writeToTextFile(fpout)


def main():
	parser = optparse.OptionParser(
		usage = "\n\t%prog [options] file ...", 
		version = "%prog 1.0")
	parser.add_option(
		'-o', '--output', 
		type = "string", dest = "output", 
		help = "specify output file")
	parser.add_option(
		'-v', '--verbose', 
		action = "store_true", dest = "verbose", default = True, 
		help = "show extra information")
	parser.add_option(
		'-q', '--quiet', 
		action = "store_false", dest = "verbose", 
		help = "no extra information")
	parser.add_option(
		'-p', '--profile', 
		action = "store_true", dest = "profile", default = False, 
		help = "collect profiling information")
	(options, args) = parser.parse_args(sys.argv[1:])

	for arg in args:
		fpin = file(arg, 'rt')

		if options.output is None:
			root, ext = os.path.splitext(arg)
			fpout = file(root + '.aterm', 'wt')
		elif options.output is '-':
			fpout = sys.stdout
		else:
			fpout = file(options.output, 'wt')

		if options.profile:
			import hotshot
			root, ext = os.path.splitext(arg)
			profname = root + '.prof'
			prof = hotshot.Profile(profname, lineevents=0)
			prof.runcall(translate, fpin, fpout, options.verbose)
			prof.close()
		else:
			translate(fpin, fpout, options.verbose)


if __name__ == '__main__':
	main()

