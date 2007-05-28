'''Module for handling assembly language code.'''


import sys
import traceback

from transf import transformation
from transf import parse

import ir.traverse
import ir.check

from machine.pentium.data import *
from machine.pentium.binary import *
from machine.pentium.logical import *
from machine.pentium.shift import *
from machine.pentium.control import *
from machine.pentium.flag import *
from machine.pentium.misc import *
from machine.pentium.simplify import simplify


class OpcodeDispatch(transf.transformation.Transformation):
	"""Transformation to quickly dispatch the transformation to the appropriate
	transformation."""

	def __init__(self):
		transf.transformation.Transformation.__init__(self)

	def apply(self, trm, ctx):
		if not trm.rmatch('Asm(_, [*])'):
			raise transf.exception.Failure

		opcode, operands = trm.args

		opcode = opcode.value
		try:
			trf = eval("asm" + opcode.upper())
		except NameError:
			sys.stderr.write("warning: don't now how to translate opcode '%s'\n" % opcode)
			raise transf.exception.Failure

		try:
			return trf.apply(operands, ctx)
		except transf.exception.Failure:
			sys.stderr.write("warning: failed to translate opcode '%s'\n" % opcode)
			traceback.print_exc()
			raise


parse.Transfs('''

doStmt =
	?Asm(opcode, _) & (
		OpcodeDispatch() +
		![<id>]
	) ;
	Try(simplify)
+	![<id>]


''', verbose=False)

module = ir.traverse.Module(
	stmts = transf.lib.lists.MapConcat(doStmt),
) #* ir.check.module


