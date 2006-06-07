'''View graphs in dot-language.'''


import gtk
import gtk.gdk

import sys
import os


class DotView(gtk.Window):
	
	# TODO: add zoom/pan as in http://mirageiv.berlios.de/
	
	def __init__(self, parent = None):
		gtk.Window.__init__(self)
		if parent is not None:
			self.set_screen(parent.get_screen())
		else:
			self.connect('destroy', gtk.main_quit)
		self.set_title('Dot')
		self.set_default_size(512, 512)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.add(scrolled_window)
		
		eventbox = gtk.EventBox()
		bgcolor = gtk.gdk.color_parse("white")
		eventbox.modify_bg(gtk.STATE_NORMAL, bgcolor)
		scrolled_window.add_with_viewport(eventbox)
			
		self.image = gtk.Image()
		eventbox.add(self.image)

		self.show_all()
	
	def set_dotcode(self, dotcode):
		
		dotin, dotout = os.popen2(['dot', '-Tsvg'], 'rw')

		dotin.write(dotcode)
		dotin.close()

		svgcode = dotout.read()
		dotout.close()

		# See images.py in pygtk demos
		pixbuf_loader = gtk.gdk.PixbufLoader('svg')
		pixbuf_loader.connect("area_prepared", self.on_pixbuf_loader_area_prepared)
		pixbuf_loader.connect("area_updated", self.on_pixbuf_loader_area_updated)
	
		pixbuf_loader.write(svgcode)
		pixbuf_loader.close()
	
	def on_pixbuf_loader_area_prepared(self, pixbuf_loader):
		pixbuf = pixbuf_loader.get_pixbuf()
		self.image.set_from_pixbuf(pixbuf)

	def on_pixbuf_loader_area_updated(self, pixbuf_loader, x, y, width, height):
		self.image.queue_draw()
		


if __name__ == '__main__':
	win = DotView()
	win.set_dotcode(sys.stdin.read())
	gtk.main()
