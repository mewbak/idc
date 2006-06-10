#!/usr/bin/env python


def main():
	import sys
	import os
	import hotshot

	if len(sys.argv) <= 1:
		print "usage: $s script ..." % os.path.basename(sys.argv[0])
		sys.exit(2)
	
	filename = sys.argv[1]
	del sys.argv[0]

	root, ext = os.path.splitext(filename)
	profname = root + '.prof'
	
	glbls = globals()
	glbls.pop('main')

	sys.path.insert(0, os.path.dirname(filename))

	prof = hotshot.Profile(profname, lineevents=0)
	prof.runcall(execfile, filename, glbls, glbls)
	prof.close()


if __name__ == '__main__':
	main()
