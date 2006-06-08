'''Debugging transformations.'''


import sys
import traceback
import inspect
import os.path

from transf import exception
from transf import base
from transf import combine


def dump_term(log, term):
	log.write("Term:\n")
	log.write("\n\t")
	try:
		term.writeToTextFile(log)
	except:
		log.write('<error>')
	log.write("\n")


def dump_context(log, context):
	log.write("Context:\n")
	for name, value in context.iteritems():
		log.write("\t%s = " % name)
		try:
			value.writeToTextFile(value)
		except:
			log.write('<error>')
		log.write("\n")

class Dump(base.Transformation):
	
	def __init__(self, log=None):
		base.Transformation.__init__(self)
		if log is None:
			self.log = sys.stderr
		else:
			self.log = log
		caller = sys._getframe(1)
		self.filename = os.path.abspath(caller.f_code.co_filename)
		self.lineno = caller.f_lineno
	
	def apply(self, term, context):
		self.log.write('File "%s", line %d\n' % (self.filename, self.lineno))
		dump_term(self.log, term)
		dump_context(self.log, context)
		return term


class Trace(combine.Unary):

	def __init__(self, name, operand, log=None):
		combine.Unary.__init__(self, operand)
		if log is None:
			self.log = sys.stderr
		else:
			self.log = log
		self.name = name

	def short_repr(self, term, trunc=40):
		r = repr(term)
		if len(r) > trunc:
			r = r[:trunc] + "..."
		return r
	
	def apply(self, term, context):
		self.log.write('=> Entering %s (%s)\n' % (self.name, self.short_repr(term)))
		#dump_term(self.log, term)
		term = self.operand.apply(term, context)
		self.log.write('<= Leaving %s\n (%s)\n' % (self.name, self.short_repr(term)))
		#dump_term(self.log, term)
		return term


class Traceback(combine.Unary):

	def __init__(self, operand, log=None):
		combine.Unary.__init__(self, operand)
		if log is None:
			self.log = sys.stderr
		else:
			self.log = log

	def apply(self, term, context):
		try:
			return self.operand.apply(term, context)
		except exception.Failure:
			e_type, e_value, tb = sys.exc_info()
			records = inspect.getinnerframes(tb, 0)
			for frame, file, lineno, func, lines, index in records:
				file = file and os.path.abspath(file) or '?'
				args, varargs, varkw, locals = inspect.getargvalues(frame)
				
				#print file, lnum, func
				#print args, varargs, varkw
				#print locals
				#print locals['self'].__class__.__name__,
			
			print
			
			print e_type, e_value
			frame, file, lineno, func, lines, index = records[-1]
			
			term = locals['term']
			context = locals['context']
			
			dump_term(self.log, term)
			dump_context(self.log, context)
			raise #exception.Failure


if __name__ == '__main__':
    trf = Trace(base.fail)
    trf.apply(None, None)