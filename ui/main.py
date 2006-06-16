"""Main window."""

# See:
# - http://www.pygtk.org/pygtk2tutorial/
# - http://www.pygtk.org/pygtk2reference/

import sys

import gtk

import locale
locale.setlocale(locale.LC_ALL,'')

import box
import ir.pprint
import model

from ui.menus import RefactorMenu, ViewMenu, PopupMenu
from ui import textbuffer


class MainApp(gtk.Window):

	ui = '''
	<ui>
		<menubar name="MenuBar">
			<menu action="FileMenu">
				<menuitem action="New"/>
				<menuitem action="Open"/>
				<menuitem action="Save"/>
				<menuitem action="SaveAs"/>
				<separator/>
				<menuitem action="Quit"/>
			</menu>
			<menu action="RefactorMenu">
				<menuitem action="Empty"/>
			</menu>
			<menu action="ViewMenu">
				<menuitem action="Empty"/>
			</menu>
			<menu action="HelpMenu">
				<menuitem action="About"/>
			</menu>
		</menubar>
	</ui>
	'''
	  
	def __init__(self):
		# Create the toplevel window
		gtk.Window.__init__(self)
		
		window = self
		
		window.connect('destroy', self.on_window_destroy)
		window.set_default_size(640, 480)
		vbox = gtk.VBox()
		window.add(vbox)

		window = self
		

		self.set_title('Interactive Decompiler')

		# Create a UIManager instance
		uimanager = gtk.UIManager()

		# Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		window.add_accel_group(accelgroup)

		# Create an ActionGroup
		actiongroup = gtk.ActionGroup('Actions')
		self.actiongroup = actiongroup

		# Create actions
		actiongroup.add_actions((
			('FileMenu', None, '_File'),
			('New', gtk.STOCK_NEW, None, None, None, self.on_new),  
			('Open', gtk.STOCK_OPEN, None, None, None, self.on_open),  
			('Save', gtk.STOCK_SAVE, None, None, None, self.on_save),
			('SaveAs', gtk.STOCK_SAVE_AS, None, None, None, self.on_save),
			('Quit', gtk.STOCK_QUIT, None, None, None, self.on_quit),  
			('RefactorMenu', None, '_Refactor'),
			('ViewMenu', None, '_View'),
			('Empty', None, 'Empty'),  
			('HelpMenu', None, '_Help'),
			('About', gtk.STOCK_ABOUT, None, None, None, self.on_about),
		))
		actiongroup.get_action('Empty').set_sensitive(False)


		# Add the actiongroup to the uimanager
		uimanager.insert_action_group(actiongroup, 0)

		# Add a UI description
		uimanager.add_ui_from_string(self.ui)

		# Create a MenuBar
		menubar = uimanager.get_widget('/MenuBar')
		vbox.pack_start(menubar, False)

		# Create a Toolbar
		#toolbar = uimanager.get_widget('/Toolbar')
		#vbox.pack_start(toolbar, False)

		textview = gtk.TextView()
		textview.connect("event", self.on_textview_button_press)
		vbox.pack_start(textview)
		self.textview = textview

		window.show_all()

		self.model = model.Model()
		self.model.term.attach(self.on_term_update)
		
		if len(sys.argv) > 1:
			self.open(sys.argv[1])
		else:
			self.model.new()
		
		refactormenu = RefactorMenu(self.model)
		uimanager.get_widget('/MenuBar/RefactorMenu').set_submenu(refactormenu)
		viewmenu = ViewMenu(self.model)
		uimanager.get_widget('/MenuBar/ViewMenu').set_submenu(viewmenu)

	def main(self):
		"""Enter main loop."""
		gtk.main()

	def quit(self, *args):
		"""Quit main loop."""
		gtk.main_quit()
	
	def on_new(self, action):
		self.model.new()
	
	def on_open(self, action):
		path = self.run_open_dialog(
				None, 
				self, 
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

	def on_save(self, action):
		# FIXME: implement this
		pass
	
	def on_saveas(self, action):
		path = self.run_saveas_dialog(
				None, 
				self, 
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

	def on_quit(self, action):
		self.quit()

	def on_window_destroy(self, event):
		self.quit()
		
	def on_about(self, action):
		aboutdialog = gtk.AboutDialog()
		aboutdialog.set_name('IDC')
		#aboutdialog.set_version()
		aboutdialog.set_comments('An Interactive Decompiler.')
		#aboutdialog.set_license()
		aboutdialog.set_authors([u'Jos\u00e9 Fonseca <j_r_fonseca@yahoo.co.uk>'])
		#aboutdialog.set_website('http://')
		aboutdialog.run()
		aboutdialog.destroy()
		
	def on_textview_button_press(self, textview, event):
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
		
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			popupmenu = PopupMenu(self.model)
			popupmenu.popup( None, None, None, event.button, event.time)
			return True
		
		return False
		
	def get_path_at_iter(self, iter):
		for tag in iter.get_tags():
			path = tag.get_data('path')
			if path is not None:
				return path
		return None

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
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK),
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
