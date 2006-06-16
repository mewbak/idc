"""Data model."""

# TODO: move this module into a UI-independent package?


import observer

import aterm.factory
import ir.path
import ir.pprint
import box


# TODO: user more versatile signal notification (a la GObject)

class TermState(observer.State):
	"""Intermediate representation of the program using aterms."""
	
	def set(self, value):
		# Always keep an annotated term
		value = ir.path.annotate(value)
		observer.State.set(self, value)


class SelectionState(observer.State):
	"""Path tuple describing the current selection."""
	
	def __init__(self, term):
		observer.State.__init__(self)
		self.reset()
		term.attach(self.on_term_update)
		
	def reset(self):
		factory = aterm.factory.Factory()
		path = factory.makeNil()
		self.set((path, path))
		
	def on_term_update(self, program):
		self.reset()


class Model:
	"""Data model."""
	
	def __init__(self):
		self.factory = aterm.factory.Factory()
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
		self.term.set(term)

	def save_ir(self, filename):
		"""Save a text file with the intermediate representation."""
		term = self.term.get()
		fp = file(filename, 'wt')
		term.writeToTextFile(fp)

	def export_c(self, filename):
		"""Export C code."""
		term = self.term.get()
		fp = file(filename, 'wt')
		boxes = ir.pprint.module(term)
		formatter = box.TextFormatter(fp)
		writer = box.Writer(formatter)
		writer.write(boxes)

	# TODO: Write a PDF exporter, probably using latex.
	
	def apply_refactoring(self, refactoring, args):
		"""Apply a refactoring."""
		term = self.term.get()
		term = refactoring.apply(term, args)
		self.term.set(term)
		# TODO: keep an history
