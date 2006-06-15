'''View support.
'''


class View:
	
	def __init__(self, model):
		self.model = model
	
	def get_name(self):
		raise NotImplementedError
	
	def destroy(self):
		raise NotImplementedError


class ViewFactory:
	"""Base class for model views."""

	def __init__(self):
		pass
	
	def get_name(self):
		raise NotImplementedError

	def is_applicable(self, model):
		raise NotImplementedError

	def create(self, model):
		raise NotImplementedError


def main(cls):
	'''Simple main function to test views.'''
	
	import sys
	import gtk
	import aterm.factory
	import ui.document
	
	factory = aterm.factory.Factory()
	term = factory.readFromTextFile(sys.stdin)
	model = ui.document.Document()
	model.term.set(term)
	view = cls(model)
	view.connect('destroy', gtk.main_quit)
	gtk.main()