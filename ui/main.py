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
		'''Update the selection paths.'''
		
		buffer = textview.get_buffer()
					
		if \
				(event.type == gtk.gdk.BUTTON_RELEASE and event.button == 1) or \
				(event.type == gtk.gdk.BUTTON_PRESS and event.button == 3) :
			
			try:
				start, end = buffer.get_selection_bounds()
			except ValueError:
				# If there is nothing selected, None is return
				x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
				iter = textview.get_iter_at_location(x, y)
				path = self.get_path_at_iter(iter)
				self.document.selection.set((path, path))
			else:
				start = self.get_path_at_iter(start)
				end = self.get_path_at_iter(end)
				self.document.selection.set((start, end))
			
		return False

	def on_textview_populate_popup(self, textview, menu):
		'''Populate the textview popup menu.'''
		
		popup = gtk.Menu()
		
		term = self.document.term.get()
		selection = self.document.selection.get()
		
		for refactoring in self.refactoring_factory.refactorings.itervalues():
			menuitem = gtk.MenuItem(refactoring.name())
			if refactoring.applicable(term, selection):
				menuitem.connect("activate", self.on_menuitem_activate, refactoring)
			else:
				menuitem.set_state(gtk.STATE_INSENSITIVE)
			menuitem.show()
			popup.append(menuitem)
	
		menuitem = gtk.MenuItem()
		menuitem.show()
		menu.prepend(menuitem)

		menuitem = gtk.MenuItem("Refactor")
		menuitem.set_submenu(popup)
		menuitem.show()
		menu.prepend(menuitem)
		
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

