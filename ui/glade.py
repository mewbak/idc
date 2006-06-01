"""Common classes for handling glade-based windows."""

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/


import gtk
import gtk.glade

import gettext
import os.path


class GladeWindow:
	"""Base class for glade based windows."""

	# See: 
	# - http://www.jamesh.id.au/software/libglade/
	# - http://www.pygtk.org/pygtk2reference/class-gladexml.html
	# - http://www.pixelbeat.org/libs/libglade.py

	def __init__(self, filename, windowname):
		"""Load glade file."""

		filename = os.path.join(os.path.dirname(__file__), filename)
	
		self.xml = gtk.glade.XML(filename, windowname, gettext.textdomain())
		self.widget = self.xml.get_widget(windowname)
		
		self._signal_autoconnect()

	def _signal_autoconnect(self):
		'''Auto-connect signals using introspection.'''
		
		# this matches the attribute names with the signal handler names given in the
		# glade file
		#self.xml.signal_autoconnect(self)
		
		# this automatically recognize signal handlers names which look as
		# "(on_|after_)_widgetname_signalname"
		on_handler_names = []
		after_handler_names = []
		for name in dir(self.__class__):
			if name.startswith('on_'):
				on_handler_names.append(name)
			if name.startswith('after_'):
				after_handler_names.append(name)
		
		for widget in self.xml.get_widget_prefix(""):
			widget_name = gtk.glade.get_widget_name(widget)
			
			prefix = 'on_' + widget_name + '_'
			for name in on_handler_names:
				if name.startswith(prefix):
					signal = name[len(prefix):]
					try:
						widget.connect(signal, getattr(self, name))
					except TypeError:
						pass
					
			prefix = 'after_' + widget_name + '_'
			for name in after_handler_names:
				if name.startswith(prefix):
					signal = name[len(prefix):]
					try:
						widget.connect_after(signal, getattr(self, name))
					except TypeError:
						pass
			
		
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
	
	def run_open_dialog(self, title = None, parent = None, filters = None, folder = None):
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

	def run_saveas_dialog(self, title = None, parent = None, filters = None, folder = None):
		"""Display a file save as dialog."""

		# TODO: include a combo box with file types

		dialog = gtk.FileChooserDialog(
				title,
				parent,
				gtk.FILE_CHOOSER_ACTION_SAVE,
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
