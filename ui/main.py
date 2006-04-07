#!/usr/bin/env python

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/

import gtk
import gtk.glade

import locale
locale.setlocale(locale.LC_ALL,'')

import gettext

import os.path


import aterm
import ir
import box


class GladeWindow:
	"""Base class for glade based windows."""

	# See: 
	# - http://www.jamesh.id.au/software/libglade/
	# - http://www.pygtk.org/pygtk2reference/class-gladexml.html
	# - http://www.pixelbeat.org/libs/libglade.py

	def __init__(self, filename, windowname):
		"""Load glade file."""

		self.xml = gtk.glade.XML(filename, windowname, gettext.textdomain())

		#handlers = {}
		#for name in dir(self.__class__):
		#	handlers[name] = getattr(self, name)
		#self.xml.signal_autoconnect(handlers)
		self.xml.signal_autoconnect(self)
		
		self.widget = self.xml.get_widget(windowname)

	def __getattr__(self, name): 
		"""Allow glade widgets to be acessed as attributes."""

		widget = self.xml.get_widget(name)
		if widget is None:
			raise AttributeError, "widget %s not found" % name

		# cache reference
		setattr(self, name, widget)

		return widget


class GladeApp(GladeWindow):
	"""Base class for glade based applications."""

	def main(self):
		"""Enter main loop."""

		gtk.main()

	def quit(self, *args):
		"""Quit main loop."""

		gtk.main_quit()
				
	def open(self, title = None, parent = None, filters = None, folder = None):
		"""Display a file open dialog."""

		# See http://www.pygtk.org/pygtk2tutorial/sec-FileChoosers.html

		dialog = gtk.FileChooserDialog(
				title,
				parent,
				gtk.FILE_CHOOSER_ACTION_OPEN,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK),
		)
		dialog.set_default_response(gtk.RESPONSE_OK)

		if filters is not None:
			for name, patterns in filters:
				filter = gtk.FileFilter()
				filter.set_name(name)
				for pattern in patterns:
					filter.add_pattern(pattern)
				dialog.add_filter(filter)

		if folder is not None:
				dialog.set_current_folder(os.path.abspath(folder))

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			path = dialog.get_filename()
		else:
			path = None

		dialog.destroy()
		return path


class MainApp(GladeApp):

	def __init__(self):
		GladeApp.__init__(self, "./ui/main.glade", "main_window")
		
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


if __name__ == '__main__':
	app = MainApp()
	app.main()

