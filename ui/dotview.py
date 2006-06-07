'''View graphs in dot-language.'''


import gtk
import gtk.gdk

import sys
import os


class DotView(gtk.Window):

	def __init__(self, parent = None):
		gtk.Window.__init__(self)

		self.set_title('Dot')
		self.set_default_size(500, 500)
		self.connect('delete-event', gtk.main_quit)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.add(scrolled_window)

		self.image = gtk.Image()
		scrolled_window.add_with_viewport(self.image)

		#self.set_property('allow-grow', False)
		
		self.show_all()
	
	def set_dotcode(self, dotcode):
		
		dotin, dotout = os.popen2(['dot', '-Tsvg'], 'rw')

		dotin.write(dotcode)
		dotin.close()

		svgcode = dotout.read()
		dotout.close()

		# See images.py in pygtk demos
		self.pixbuf_loader = gtk.gdk.PixbufLoader('svg')
		self.pixbuf_loader.connect("area_prepared", self.on_pixbuf_loader_area_prepared, self.image)
		self.pixbuf_loader.connect("area_updated", self.on_pixbuf_loader_area_updated, self.image)
	
		self.pixbuf_loader.write(svgcode)
		self.pixbuf_loader.close()
	
	def on_pixbuf_loader_area_prepared(self, loader, image):
		print "area_prepared"
		pixbuf = loader.get_pixbuf()
		#pixbuf.fill(0)
		image.set_from_pixbuf(pixbuf)

	def on_pixbuf_loader_area_updated(self, loader, x, y, width, height, image):
		print "area_updated"
		#self.set_geometry_hints(max_width = width, max_height = height)
		image.queue_draw()


if __name__ == '__main__':
	win = DotView()
	win.set_dotcode(sys.stdin.read())
	gtk.main()
