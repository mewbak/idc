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

import box
import ir.pprint
import model
import refactoring

from ui import textbuffer
from ui import termview
from ui import dotview
from ui import inputter


class MainApp(glade.GladeApp):

	def __init__(self):
		glade.GladeApp.__init__(self, "main.glade", "main_window")
		
		self.model = model.Model()
		self.model.term.attach(self.on_term_update)
		
		self.refactoring_factory = refactoring.Factory()
		
		if len(sys.argv) > 1:
			self.open(sys.argv[1])
		else:
			self.model.new()

	def on_new_activate(self, event):
		self.model.new()
	
	def on_open_activate(self, event):
		path = self.run_open_dialog(
				None, 
				self.widget, 
				[
					('Assembly Files', ['*.s', '*.asm']),
					('Decompilation Projects', ['*.aterm']),
					('All Files', ['*']),
				], 
				'./examples',
		)
		self.open(path)
	
	def open(self, path):
		if path is not None:
			if path.endswith('.s'):
				self.model.open_asm(path)
			if path.endswith('.aterm'):
				self.model.open_ir(path)

	def on_save_activate(self, event):
		# FIXME: implement this
		pass
	
	def on_saveas_activate(self, event):
		path = self.run_saveas_dialog(
				None, 
				self.widget, 
				[
					('Decompilation Project', ['*.aterm']),
					('C Source File', ['*.c']),
					('All Files', ['*']),
				], 
				'./examples',
		)
		
		if path is not None:
			if path.endswith('.aterm'):
				self.model.save_ir(path)
			if path.endswith('.c'):
				self.model.export_c(path)

	def on_term_update(self, term):
		term = term.get()
		boxes = ir.pprint.module(term)
		buffer = self.textview.get_buffer()
		formatter = textbuffer.TextBufferFormatter(buffer)
		writer = box.Writer(formatter)
		writer.write(boxes)

	def on_quit_activate(self, event):
		self.quit()

	def on_viewterm_activate(self, event):
		termview.TermView(self.model)

	def on_viewcfg_activate(self, event):
		dotview.CfgView(self.model)

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
				self.model.selection.set((path, path))
			else:
				start = self.get_path_at_iter(start)
				end = self.get_path_at_iter(end)
				self.model.selection.set((start, end))
			
		return False

	def on_textview_populate_popup(self, textview, menu):
		'''Populate the textview popup menu.'''
		
		popup = gtk.Menu()
		
		term = self.model.term.get()
		selection = self.model.selection.get()
		
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
		args = refactoring.input(
			self.model.term.get(), 
			self.model.selection.get(),
			inputter.Inputter()
		)
		
		self.model.apply_refactoring(refactoring, args)
		
	def get_path_at_iter(self, iter):
		for tag in iter.get_tags():
			path = tag.get_data('path')
			if path is not None:
				return path
		return None

