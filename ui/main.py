"""Main window."""

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/

import gtk
import gtk.glade

import locale
locale.setlocale(locale.LC_ALL,'')

import glade

import ir
import box
import model

import inspector
import textbuffer


class MainApp(glade.GladeApp):

	def __init__(self):
		glade.GladeApp.__init__(self, "./ui/main.glade", "main_window")
		
		self.model = model.ProgramModel()
		
		self.model.attach(self)
		self.update(model)
		
		self.inspector = inspector.InspectorWindow(self.model)

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
			self.model.open_asm(path)

	def update(self, subject):
		self.update_textview()

	def update_textview(self):
		term = self.model.get_term()
		boxes = ir.prettyPrint(term)
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


