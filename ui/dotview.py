'''View graphs in dot-language.'''


import sys
import os
import re
import tempfile

import gtk
import gtk.gdk

import ir.cfg
import lang.dot
from ui import view


DOT = 'dot'
FORMAT = 'png'


class Area:
	
	def __init__(self, url):
		self.url = url
	
	def hit(self, x, y):
		raise NotImplementedError


class RectArea(Area):
	
	def __init__(self, url, points):
		Area.__init__(self, url)
		(self.x1, self.y1), (self.x2, self.y2) = points

	def hit(self, x, y):
		return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


class Imap:
	"""Imagemap parsing and click detection.
	
	See http://hoohoo.ncsa.uiuc.edu/docs/tutorials/imagemapping.html and 
	http://hoohoo.ncsa.uiuc.edu/docs/tutorials/imagemap.txt for implementation 
	details.
	"""
	
	types = {
		'rect': RectArea,
	}
	
	def __init__(self):
		self.default_url = None
		self.areas = []
	
	def read(self, fp):
		for line in fp:
			if line.startswith('#'):
				continue
			try:
				parts = line.split()
				type, url = parts[:2]
				points = [tuple(map(int, point.split(','))) for point in parts[2:]]
				if type == 'default':
					self.default_url = url
				else:
					cls = self.types[type]
					self.areas.append(cls(url, points))
			except KeyError:
				pass
			except:
				raise

	def hit(self, x, y):
		for area in self.areas:
			if area.hit(x, y):
				return area.url
		return self.default_url
		

class DotWindow(gtk.Window):
	
	# TODO: add zoom/pan as in http://mirageiv.berlios.de/

	ui = '''
	<ui>
		<toolbar name="ToolBar">
			<toolitem action="ZoomIn"/>
			<toolitem action="ZoomOut"/>
			<toolitem action="ZoomFit"/>
			<toolitem action="Zoom100"/>
		</toolbar>
	</ui>
	'''
	  
	hand_cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
	regular_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)

	def __init__(self):
		gtk.Window.__init__(self)

		window = self
		
		window.set_title('Dot')
		window.set_default_size(512, 512)
		vbox = gtk.VBox()
		window.add(vbox)

		# Create a UIManager instance
		uimanager = self.uimanager = gtk.UIManager()

		# Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		window.add_accel_group(accelgroup)

		# Create an ActionGroup
		actiongroup = gtk.ActionGroup('Actions')
		self.actiongroup = actiongroup

		# Create actions
		actiongroup.add_actions((
			('ZoomIn', gtk.STOCK_ZOOM_IN, None, None, None, self.on_zoom_in),  
			('ZoomOut', gtk.STOCK_ZOOM_OUT, None, None, None, self.on_zoom_out),  
			('ZoomFit', gtk.STOCK_ZOOM_FIT, None, None, None, self.on_zoom_fit),  
			('Zoom100', gtk.STOCK_ZOOM_100, None, None, None, self.on_zoom_100),  
		))

		# Add the actiongroup to the uimanager
		uimanager.insert_action_group(actiongroup, 0)

		# Add a UI description
		uimanager.add_ui_from_string(self.ui)

		# Create a Toolbar
		toolbar = uimanager.get_widget('/ToolBar')
		vbox.pack_start(toolbar, False)

		scrolled_window = self.scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.pack_start(scrolled_window)

		eventbox = gtk.EventBox()
		bgcolor = gtk.gdk.color_parse("white")
		eventbox.modify_bg(gtk.STATE_NORMAL, bgcolor)
		scrolled_window.add_with_viewport(eventbox)
			
		self.image = gtk.Image()
		eventbox.add(self.image)
		
		self.imap = None
		
		eventbox.set_above_child(True)
		eventbox.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
		#eventbox.connect("button-press-event", self.on_eventbox_button_press)
		eventbox.connect("event-after", self.on_eventbox_button_press)
		eventbox.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
		eventbox.connect("motion-notify-event", self.on_eventbox_motion_notify)
		
		self.zoom_ratio = 1.0
		self.pixbuf = None
		
		self.show_all()
	
	def write_dotcode(self, writer_cb, *args):
		# TODO: return the dotin stream
		
		# See images.py in pygtk demos
		pixbuf_loader = gtk.gdk.PixbufLoader(FORMAT)
		pixbuf_loader.connect('area_prepared', self.on_pixbuf_loader_area_prepared)
		pixbuf_loader.connect('area_updated', self.on_pixbuf_loader_area_updated)
	
		mapfd, mapname = tempfile.mkstemp('.map')
		os.close(mapfd)
		
		dotin, dotout = os.popen2([
			DOT, 
			'-Timap', '-o' + mapname,
			'-T' + FORMAT
		], 'rw')

		writer_cb(dotin, *args)
		dotin.close()

		while True:
			buf = dotout.read(8192)
			if not buf:
				break
			pixbuf_loader.write(buf)
		dotout.close()
		
		self.imap = Imap()
		self.imap.read(file(mapname, 'rt'))
		os.unlink(mapname)
		
		pixbuf_loader.close()
	
	def set_dotcode(self, dotcode):
		self.write_dotcode(lambda fp: fp.write(dotcode))
	
	def set_graph(self, graph):
		self.write_dotcode(lambda fp: lang.dot.write(graph, fp))
		
	def on_pixbuf_loader_area_prepared(self, pixbuf_loader):
		self.pixbuf = pixbuf_loader.get_pixbuf()

	def on_pixbuf_loader_area_updated(self, pixbuf_loader, x, y, width, height):
		self.zoom_image()
		self.image.queue_draw()
	
	def zoom_image(self):
		if self.pixbuf:
			if self.zoom_ratio == 1.0:
				self.image.set_from_pixbuf(self.pixbuf)
			else:
				w = int(self.pixbuf.get_width() * self.zoom_ratio)
				h = int(self.pixbuf.get_height() * self.zoom_ratio)
				scaled_pixbuf = self.pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
				self.image.set_from_pixbuf(scaled_pixbuf)
  	
	def on_zoom_in(self, action):
		self.zoom_ratio *= 1.25
		self.zoom_image()
		
	def on_zoom_out(self, action):
		self.zoom_ratio *= 1/1.25
		self.zoom_image()
		
	def on_zoom_fit(self, action):
		imgwidth, imgheight = self.scrolled_window.window.get_size()
		pixwidth = self.pixbuf.get_width()
		pixheight = self.pixbuf.get_height()
		self.zoom_ratio = min(
			float(imgwidth)/float(pixwidth), 
			float(imgheight)/float(pixheight)
		)
		self.zoom_image()
		
	def on_zoom_100(self, action):
		self.zoom_ratio = 1.0
		self.zoom_image()
		
	def on_eventbox_button_press(self, eventbox, event):
		if not self.pixbuf:
			return False
		if event.type not in (gtk.gdk.BUTTON_PRESS, gtk.gdk.BUTTON_RELEASE):
			return False
		x, y = int(event.x), int(event.y)
		url = self.get_url(x, y)
		if url is not None:
			return self.on_url_clicked(url, event)
		return False

	def on_eventbox_motion_notify(self, eventbox, event):
		if not self.pixbuf:
			return False
		x, y = int(event.x), int(event.y)
		if self.get_url(x, y) is not None:
			eventbox.window.set_cursor(self.hand_cursor)
		else:
			eventbox.window.set_cursor(self.regular_cursor)
		return False
		
	def get_url(self, x, y):
		imgwidth, imgheight = self.image.window.get_size()
		pixbuf = self.image.get_pixbuf()
		pixwidth = pixbuf.get_width()
		pixheight = pixbuf.get_height()
	
		# NOTE: we assume were 0.5 alignment and 0 padding
		x -= (imgwidth - pixwidth) / 2
		y -= (imgheight - pixheight) / 2
		x /= self.zoom_ratio
		y /= self.zoom_ratio
		#assert 0 <= x <= imgwidth
		#assert 0 <= y <= imgheight

		if self.imap is not None:
			return self.imap.hit(x, y)
		return None
		
	def on_url_clicked(self, url, event):
		return False


class DotView(DotWindow, view.View):
	
	def __init__(self, model):
		DotWindow.__init__(self)
		view.View.__init__(self, model)
	
		model.connect('notify::term', self.on_term_update)

		self.connect('destroy', self.on_window_destroy)
		
		if model.get_term() is not None:
			self.on_term_update(model.term)

	def get_name(self, name):
		return 'Dot View'
		
	def on_term_update(self, term):
		pass

	def on_window_destroy(self, event):
		model = self.model
		model.disconnect('notify::term', self.on_term_update)
	
	def on_url_clicked(self, url, event):
		model = self.model
		term = model.get_term()
		factory = term.factory
		path = factory.parse(url)
		return self.on_path_clicked(path, event)
	
	def on_path_clicked(self, path, event):
		if event.type == gtk.gdk.BUTTON_RELEASE and event.button == 1:
			self.model.set_selection((path, path))
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			self.model.set_selection((path, path))
			from ui.menus import PopupMenu
			popupmenu = PopupMenu(self.model)
			popupmenu.popup( None, None, None, event.button, event.time)			
		return True


class CfgView(DotView):

	def __init__(self, model):
		DotView.__init__(self, model)
		self.set_title('Control Flow Graph')
		
	def on_term_update(self, term):
		graph = ir.cfg.render(term)
		self.set_graph(graph)


class CfgViewFactory(view.ViewFactory):
	
	def get_name(self):
		return 'Control Flow Graph'
	
	def can_create(self, model):
		return True
	
	def create(self, model):
		return CfgView(model)
	

if __name__ == '__ma in__':
	win = DotWindow()
	win.set_dotcode(sys.stdin.read())
	win.connect('destroy', gtk.main_quit)
	gtk.main()


if __name__ == '__main__':
	view.main(CfgView)
