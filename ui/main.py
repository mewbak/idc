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
import path

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
	
	def open(self, filename):
		# TODO: catch exceptions here
		from machine.pentium import Pentium
		machine = Pentium()

		term = machine.load(self.factory, file(filename, 'rt'))
		term = machine.translate(term)
		term = path.Annotator(term.factory).anno(term)
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

	def on_textview_event_after(self, textview, event):
		if event.type != gtk.gdk.BUTTON_RELEASE:
			return False
		if event.button != 1:
			return False
		buffer = textview.get_buffer()

		# we shouldn't follow a link if the user has selected something
		try:
			start, end = buffer.get_selection_bounds()
		except ValueError:
			# If there is nothing selected, None is return
			pass
		else:
			if start.get_offset() != end.get_offset():
				return False

		x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
		iter = textview.get_iter_at_location(x, y)

		for tag in iter.get_tags():
			path = tag.get_data('path')
			if path is not None:
				print path
				dialog = gtk.MessageDialog(
					parent=None, 
					flags=0, 
					type=gtk.MESSAGE_INFO, 
					buttons=gtk.BUTTONS_OK, 
					message_format=str(path)
				)
				dialog.run()
				dialog.destroy()
		return False


