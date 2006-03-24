#!/usr/bin/env python

import gtk
import gtk.glade

import locale
locale.setlocale(locale.LC_ALL,'')

import gettext


class GladeWindow:
	"""
	Superclass for glade based applications. Just derive from this
	and your subclass should create methods whose names correspond to
	the signal handlers defined in the glade file. Any other attributes
	in your class will be safely ignored.

	This class will give you the ability to do:
		subclass_instance.window.method(...)
		subclass_instance.widget_name...

	Based on http://www.pixelbeat.org/libs/libglade.py
	"""

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

	def main(self):
		gtk.main()

	def quit(self, *args):
		gtk.main_quit()
				

class MainApp(GladeApp):

	def __init__(self):
		GladeApp.__init__(self, "./idc.glade", "main_window")

	def on_quit_activate(self, event):
		self.quit()

	def on_main_window_destroy(self, event):
		self.quit()



if __name__ == '__main__':
	app = MainApp()
	app.main()

