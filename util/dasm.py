#!/usr/bin/env python

import sys
import optparse
import subprocess
import re


def dasm(infile, outfp, verbose = True):

	command_line = [
		'objdump',
		'--disassemble',
		'--disassemble-zeroes',
		'--disassembler-options=att,suffix',
		'--prefix-addresses',
		'--no-show-raw-insn',
		'--wide',
		infile
	]
	p = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=False)
	infp = p.stdout

	for line in infp:
		if line == "Disassembly of section .text:\n":
			break

	insns = []
	addrs = set()
	for line in infp:
		line = line[:-1]
		if not line:
			break
		addr, insn = line.split(" ", 1)
		if insn.strip() == "(bad)":
			continue
		insns.append((addr, insn))
		addrs.add(addr)

	def repl(mo):
		addr = mo.group()
		if addr in addrs:
			return "loc" + addr[2:]
		else:
			return addr

	for addr, insn in insns:
		insn = re.sub(r'\b0x[0-9a-fA-F]+\b', repl, insn)
		addr = "loc" + addr[2:]
		outfp.write("%s: %s\n" % (addr, insn))


def main():
	parser = optparse.OptionParser(
		usage = "\n\t%prog [options] executable ...",
		version = "%prog 1.0")
	parser.add_option(
		'-o', '--output',
		type = "string", dest = "output",
		help = "specify output assembly file")
	parser.add_option(
		'-v', '--verbose',
		action = "count", dest = "verbose", default = 1,
		help = "show extra information")
	parser.add_option(
		'-q', '--quiet',
		action = "store_const", dest = "verbose", const = 0,
		help = "no extra information")
	(options, args) = parser.parse_args(sys.argv[1:])

	for arg in args:
		if options.output is None:
		#	root, ext = os.path.splitext(arg)
		#	fpout = file(root + '.s', 'wt')
		#elif options.output is '-':
			fpout = sys.stdout
		else:
			fpout = file(options.output, 'wt')

		dasm(arg, fpout, options.verbose)


if __name__ == '__main__':
	main()

