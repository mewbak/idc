"""Data model."""


import observer

import aterm
import ir
import path


class Model(observer.Subject):
	"""Data model class. It subclasses the subject class from the observer 
	pattern, so that it is easy to maintain up-to-date views of the data.
	"""
	
	def __init__(self, term):
		observer.Subject.__init__(self)
		self._term = term
		
	def get_term(self):
		return self._term
	
	def set_term(self, term):
		term = path.Annotator.annotate(term)
		self._term = term
		self.notify()


class ProgramModel(Model):
	"""Program data model."""
	
	def __init__(self):
		self.factory = aterm.Factory()
		term = self.factory.parse('Module([])')
		Model.__init__(self, term)
	
	def new(self):
		term = self.factory.parse('Module([])')
		self.set_term(term)
		
	def open_asm(self, filename):
		"""Open an assembly file."""
		# TODO: catch exceptions here
		from machine.pentium import Pentium
		machine = Pentium()
		term = machine.load(self.factory, file(filename, 'rt'))
		term = machine.translate(term)
		self.set_term(term)
	
	def open_ir(self, filename):
		"""Open a text file with the intermediate representation."""
		fp = file(filename, 'rt')
		term = self.factory.readFromTextFile(fp)
		self.set_term(term)

	def save_ir(self, filename):
		"""Save a text file with the intermediate representation."""
		fp = file(filename, 'wt')
		self.term.writeToTextFile(fp)

	def save_c(self, filename):
		"""Save the C code."""
		fp = file(filename, 'wt')
		printer = ir.PrettyPrinter(term.factory)
		boxes = printer.module(term)
		formatter = box.TextFormatter(fp)
		writer = box.Writer(formatter)
		writer.write_box(boxes)

	# TODO: add a method to apply refactorings here