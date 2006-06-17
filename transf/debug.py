'''Debugging transformations.'''


import sys
import traceback
import inspect
import os.path
import time

import aterm.terms
from transf import exception
from transf import base
from transf import _operate


#############################################################################
# Automatically start the debugger on an exception.
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65287

def excepthook(type, value, tb):

	if hasattr(sys, 'ps1') \
	or not (sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()) \
	or type == SyntaxError or type == KeyboardInterrupt:
		# we are in interactive mode or we don't have a tty-like
		# device, so we call the default hook
		sys.__excepthook__(type, value, tb)
	else:
		import traceback, pdb
		# we are NOT in interactive mode, print the exception...
		traceback.print_exception(type, value, tb)
		print
		# ...then start the debugger in post-mortem mode.
		pdb.pm()

#sys.excepthook = excepthook



def dump_term(log, term):
	log.write("Term:\n")
	log.write("\n\t")
	try:
		term.writeToTextFile(log)
	except:
		log.write('<error>')
	log.write("\n")


def dump_context(log, ctx):
	log.write("Context:\n")
	for name, value in ctx:
		log.write("\t%s = " % name)
		try:
			if isinstance(value, aterm.terms.Term):
				value.writeToTextFile(log)
			else:
				log.write(repr(value))
				log.write('\n')
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
	
	def apply(self, term, ctx):
		self.log.write('File "%s", line %d\n' % (self.filename, self.lineno))
		dump_term(self.log, term)
		dump_context(self.log, ctx)
		return term


class Trace(_operate.Unary):

	def __init__(self, name, operand, log=None):
		_operate.Unary.__init__(self, operand)
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
	
	def apply(self, term, ctx):
		self.log.write('=> Entering %s: %s\n' % (self.name, self.short_repr(term)))
		#dump_term(self.log, term)
		start = time.clock()
		try:
			term = self.operand.apply(term, ctx)
		finally:
			end = time.clock()
			delta = end - start
			self.log.write('<= Leaving %s (%.03fs): %s\n' % (self.name, delta, self.short_repr(term)))
		#dump_term(self.log, term)
		return term


class Traceback(_operate.Unary):

	def __init__(self, operand, log=None):
		_operate.Unary.__init__(self, operand)
		if log is None:
			self.log = sys.stderr
		else:
			self.log = log

	def apply(self, term, ctx):
		try:
			return self.operand.apply(term, ctx)
		except exception.Failure:
			e_type, e_value, tb = sys.exc_info()
			records = inspect.getinnerframes(tb, 0)
			for frame, file, lineno, func, lines, index in records:
				file = file and os.path.abspath(file) or '?'
				args, varargs, varkw, locals = inspect.getargvalues(frame)
				
				#print file, lnum, func
				#print args, varargs, varkw
				#print locals
				print "********************************************"
				try:
					print locals['self'].__class__.__name__,
					print repr(locals['term'])[:40]
					dump_context(self.log, locals['ctx'])
				except:
					pass
			
			print
			
			print e_type, e_value
			frame, file, lineno, func, lines, index = records[-1]
			
			term = locals['term']
			ctx = locals['ctx']
			
			dump_term(self.log, term)
			dump_context(self.log, ctx)
			raise #exception.Failure


if __name__ == '__main__':
    trf = Trace(base.fail)
    trf.apply(None, None)