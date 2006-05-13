"""Main window."""

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/

import gtk
import gtk.glade

import locale
locale.setlocale(locale.LC_ALL,'')

import glade

import aterm
import ir
import box

import inspector
import textbuffer


class MainApp(glade.GladeApp):

	def __init__(self):
		glade.GladeApp.__init__(self, "./ui/main.glade", "main_window")
		
		self.factory = aterm.Factory()
		self.term = self.factory.parse("Module([])")
		
		self.inspector = inspector.InspectorWindow(self.term)

	def on_open_activate(self, event):
		path = self.show_open(
				None, 
				self.widget, 
				[
					('Assembly Files', ['*.s']),
					('All Files', ['*']),
				], 
				'./examples',
		)
		
		if path is not None:
			self.open(path)
	
	def open(self, path):
		# TODO: catch exceptions here
		from machine.pentium import Pentium
		machine = Pentium()

		term = machine.load(self.factory, file(path, 'rt'))
		term = machine.translate(term)
		self.term = term
		
		self.update_textview()
		self.inspector.set_term(term)

	def update_textview(self):
		boxes = ir.prettyPrint(self.term)
		buffer = self.textview.get_buffer()
		formatter = textbuffer.TextBufferFormatter(buffer)
		writer = box.Writer(boxes.factory, formatter)
		writer.write_box(boxes)

	def on_quit_activate(self, event):
		self.quit()

	def on_main_window_destroy(self, event):
		self.quit()


