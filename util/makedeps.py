#!/usr/bin/env python

import sys
import re
import os.path

all = []

for arg in sys.argv[1:]:
	arg = os.path.normpath(arg)
	argdir = os.path.dirname(arg)

	depends = []
	targets = []
	depends.append(arg)
	for line in open(arg, "rt"):
		mo = re.search(r"\bclass\s+(\w+)\s+extends\s+(\w+)\s*;", line)
		if mo:
			klass = mo.group(1)
			target = os.path.join(argdir, klass + ".py")
			targets.append(target)
		mo = re.search(r"\bimportVocab\s*=\s*(\w+)\s*;", line)
		if mo:
			depend = os.path.join(argdir, mo.group(1) + "TokenTypes.txt")
			depends.append(depend)
		mo = re.search(r"\bexportVocab\s*=\s*(\w+)\s*;", line)
		if mo:
			target = os.path.join(argdir, mo.group(1) + "TokenTypes.txt")
			if target not in targets:
				targets.append(target)

	print " ".join(targets) + ': ' + " ".join(depends)
	print "\t$(ANTLR) -o $(@D) $<"
	print "\t@touch " + " ".join(targets)
	print

	all.extend(targets)

print "all: " + " ".join(all)
print
print "clean: clean-antlr"
print
print "clean-antlr:";
print "\t-$(RM) " + " ". join(all)
print
