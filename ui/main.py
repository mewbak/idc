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


class MainApp(glade.GladeApp):

	def __init__(self):
		glade.GladeApp.__init__(self, "./ui/main.glade", "main_window")
		
		self.factory = aterm.Factory()
		self.term = self.factory.parse("Module([])")

	def on_open_activate(self, event):
		path = self.open(
				None, 
				self.widget, 
				[
					('Assembly Files', ['*.s']),
					('All Files', ['*']),
				], 
				'./examples',
		)
		
		if path is not None:
			# TODO: catch exceptions here
			from machine.pentium import Pentium
			machine = Pentium()

			term = machine.load(self.factory, file(path, 'rt'))
			term = machine.translate(term)
			self.term = term
			
			self.update_textview()

	def update_textview(self):
		boxes = ir.prettyPrint(self.term)
		text = box.box2text(boxes)

		# See http://www.pygtk.org/pygtk2tutorial/sec-TextViews.html	
		textbuffer = self.textview.get_buffer()
		textbuffer.set_text(text)
		
		# FIXME: use tags and/or other source view widgets

	def on_quit_activate(self, event):
		self.quit()

	def on_main_window_destroy(self, event):
		self.quit()


