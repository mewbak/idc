'''Debugging transformations.'''


import sys
import os.path

from transf import base


class Dump(base.Transformation):
	
	def __init__(self, fp=None):
		base.Transformation.__init__(self)
		if fp is None:
			self.log = sys.stderr
		else:
			self.log = fp
		caller = sys._getframe(1)
		self.filename = os.path.abspath(caller.f_code.co_filename)
		self.lineno = caller.f_lineno
	
	def apply(self, term, context):
		self.log.write('File "%s", line %d\n' % (self.filename, self.lineno))
		self.log.write("Term:\n")
		try:
			term_repr = repr(term)
		except:
			term_repr = "<error>"
		self.log.write("\t%s\n" % term_repr)
		
		self.log.write("Context:\n")
		# TODO: sort
		for name, value in context.iteritems():
			try:
				value_repr = repr(value)
			except:
				value_repr = "<error>"
			self.log.write("\t%s = %s\n" % (name, value_repr))
		
		# TODO: callers frames

		self.log.write("\n")
		return term
		
		
