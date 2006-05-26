"""Main window."""

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/

import sys

import gtk
import gtk.glade

import locale
locale.setlocale(locale.LC_ALL,'')

import glade

import ir
import box
import document
import refactoring

from ui import inspector
from ui import textbuffer


class MainApp(glade.GladeApp):

	def __init__(self):
		glade.GladeApp.__init__(self, "./ui/main.glade", "main_window")
		
		self.document = document.Document()
		self.document.term.attach(self.on_term_update)
		
		self.refactoring_factory = refactoring.Factory()
		
		if len(sys.argv) > 1:
			self.document.open_asm(sys.argv[1])
		else:
			self.document.new()

		self.inspector_window = None

	def on_new_activate(self, event):
		self.document.new()
	
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
			self.document.open_asm(path)

	def on_term_update(self, term):
		term = term.get()
		boxes = ir.prettyPrint(term)
		buffer = self.textview.get_buffer()
		formatter = textbuffer.TextBufferFormatter(buffer)
		writer = box.Writer(boxes.factory, formatter)
		writer.write_box(boxes)

	def on_quit_activate(self, event):
		self.quit()

	def on_inspector_toggled(self, menuitem):
		"""(De)activate the inspector window."""
		if self.inspector.get_active():
			assert self.inspector_window is None
			self.inspector_window = inspector.InspectorWindow(self)
		else:
			assert self.inspector_window is not None
			self.inspector_window.widget.destroy()
			self.inspector_window = None

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
		self.document.selection.set((path, path))
		
		# See menu.py from PyGTK Tutorial
		
		popup = gtk.Menu()
		refactorings = self.refactoring_factory.applicables(self.document.term.get(), self.document.selection.get())
		empty = True
		for refactoring in refactorings:
			print refactoring.name()
			menuitem = gtk.MenuItem(refactoring.name())
			popup.append(menuitem)
			menuitem.connect("activate", self.on_menuitem_activate, refactoring)
			menuitem.show()
			empty = False
		
		if not empty:
			popup.popup(None, None, None, event.button, event.time)
		
		return True

	def on_menuitem_activate(self, menu, refactoring):
		print refactoring.name()
		
		# Ask user input
		import inputter
		args = refactoring.input(
			self.document.term.get(), 
			self.document.selection.get(),
			inputter.Inputter()
		)
		
		self.document.apply_refactoring(refactoring, args)
		
	def get_path_at_iter(self, iter):
		for tag in iter.get_tags():
			path = tag.get_data('path')
			if path is not None:
				path = self.document.factory.parse(path)
				return path
		return False

