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
		
		self.model.attach(self.update)
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

	def on_textview_event(self, textview, event):
		#if event.type != gtk.gdk.BUTTON_RELEASE:
		if event.type != gtk.gdk.BUTTON_PRESS:
			return False
		if event.button != 3:
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
				#return False
				pass

		x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
		iter = textview.get_iter_at_location(x, y)

		path = self.get_path_at_iter(iter)
		if 0: #path is not None:
			dialog = gtk.MessageDialog(
				parent=None, 
				flags=0, 
				type=gtk.MESSAGE_INFO, 
				buttons=gtk.BUTTONS_OK, 
				message_format=str(path)
			)
			dialog.run()
			dialog.destroy()
		print path
		self.model.selection.set_selection(path, path)
		return False

	def get_path_at_iter(self, iter):
		for tag in iter.get_tags():
			path = tag.get_data('path')
			if path is not None:
				path = self.model.factory.parse(path)
				return path
		return False

