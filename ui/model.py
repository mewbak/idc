"""Data model."""


import aterm.factory
import aterm.term
import ir.path
import ir.pprint
from lang import box


_factory = aterm.factory.factory


class Model:
	"""Abstract model."""
	
	# TODO: this is obviously GObject inspired -- should we subclass from it?
	# See http://www.sicem.biz/personal/lgs/docs/gobject-python/gobject-tutorial.html
	
	def __init__(self):
		self._signal_handlers = {}
		self._default_term = _factory.parse('Module([])')
		self._default_selection = _factory.makeNil(), _factory.makeNil()
		self._term = self._default_term
		self._selection = self._default_selection

	def connect(self, signal, handler, *args):
		handlers = self._signal_handlers.setdefault(signal, [])
		handlers.append((handler, args))
		
	def notify(self, signal, obj):
		for handler, args in self._signal_handlers.get(signal, []):
			handler(obj, *args)
	
	def disconnect(self, signal, handler):
		handlers = self._signal_handlers.get(signal, [])
		handlers = [(handler_, args) for handler_, args in handlers if handler_ != handler]
		self._signal_handlers[signal] = handlers
		
	def get_term(self):
		return self._term

	def set_term(self, term):
		# keep term paths annotated
		self._term = ir.path.annotate(term)
		self._selection = self._default_selection
		self.notify('notify::term', self._term)
		self.notify('notify::selection', self._selection)
		self.notify('notify', self)

	term = property(get_term, set_term)

	def get_selection(self):
		return self._selection
	
	def set_selection(self, selection):
		self._selection = selection
		self.notify('notify::selection', self._selection)
		self.notify('notify', self)

	selection = property(get_selection, set_selection)

	def new(self):
		"""New document."""
		self.set_term(self._default_term)
		
	def open_asm(self, filename):
		"""Open an assembly file."""
		# TODO: be machine independent
		from machine.pentium import Pentium
		machine = Pentium()
		# TODO: catch exceptions here
		term = machine.load(_factory, file(filename, 'rt'))
		term = machine.translate(term)
		self.set_term(term)
	
	def open_ir(self, filename):
		"""Open a text file with the intermediate representation."""
		fp = file(filename, 'rt')
		term = _factory.readFromTextFile(fp)
		self.set_term(term)

	def save_ir(self, filename):
		"""Save a text file with the intermediate representation."""
		term = self.get_term()
		fp = file(filename, 'wt')
		term.writeToTextFile(fp)

	def export_c(self, filename):
		"""Export C code."""
		term = self.get_term()
		fp = file(filename, 'wt')
		boxes = ir.pprint.module(term)
		formatter = box.TextFormatter(fp)
		writer = box.Writer(formatter)
		writer.write(boxes)

	# TODO: Write a PDF exporter, probably using latex.
	
	def apply_refactoring(self, refactoring, args):
		"""Apply a refactoring."""
		term = self.get_term()
		term = refactoring.apply(term, args)
		self.set_term(term)
		# TODO: keep an history
