"""Document data model."""


import observer

import aterm
import ir
import path


class TermState(observer.State):
	"""Intermediate representation of the program using aterms."""
	
	def set(self, value):
		value = path.Annotator.annotate(value)
		observer.State.set(self, value)


class SelectionState(observer.State):
	"""Path tuple describing the current selection."""
	
	def __init__(self, term):
		observer.State.__init__(self)
		self.reset()
		term.attach(self.on_term_update)
		
	def reset(self):
		self.set((None, None))
		
	def on_term_update(self, program):
		self.reset()


class Document:
	"""Document data model."""
	
	def __init__(self):
		self.factory = aterm.Factory()
		self.term = TermState()
		self.selection = SelectionState(self.term)
		
	def new(self):
		"""New document."""
		term = self.factory.parse('Module([])')
		self.term.set(term)
		
	def open_asm(self, filename):
		"""Open an assembly file."""
		# TODO: catch exceptions here
		from machine.pentium import Pentium
		machine = Pentium()
		term = machine.load(self.factory, file(filename, 'rt'))
		term = machine.translate(term)
		self.term.set(term)
	
	def open_ir(self, filename):
		"""Open a text file with the intermediate representation."""
		fp = file(filename, 'rt')
		term = self.factory.readFromTextFile(fp)
		self.set_term(term)

	def save_ir(self, filename):
		"""Save a text file with the intermediate representation."""
		term = self.term.get()
		fp = file(filename, 'wt')
		term.writeToTextFile(fp)

	def export_c(self, filename):
		"""Export C code."""
		term = self.term.get()
		fp = file(filename, 'wt')
		printer = ir.PrettyPrinter(term.factory)
		boxes = printer.module(term)
		formatter = box.TextFormatter(fp)
		writer = box.Writer(formatter)
		writer.write_box(boxes)

	# TODO: Write a PDF exporter, probably using latex.
	
	def apply_refactoring(self, refactoring, args):
		"""Apply a refactoring."""
		term = self.term.get()
		term = refactoring.apply(term, args)
		self.term.set(term)
		# TODO: keep an history
