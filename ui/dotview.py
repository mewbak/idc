'''View graphs in dot-language.'''


import sys
import os

import gtk
import gtk.gdk

import ir.cfg
import lang.dot
from ui import view


DOT = 'dot'
FORMAT = 'png'


class DotWindow(gtk.Window):
	
	# TODO: add zoom/pan as in http://mirageiv.berlios.de/
	# TODO: use maps to detect clicks in nodes as in http://hoohoo.ncsa.uiuc.edu/docs/tutorials/imagemapping.html
	
	def __init__(self):
		gtk.Window.__init__(self)

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
	
	def write_dotcode(self, writer_cb, *args):
		# TODO: return the dotin stream
		
		# See images.py in pygtk demos
		pixbuf_loader = gtk.gdk.PixbufLoader(FORMAT)
		pixbuf_loader.connect('area_prepared', self.on_pixbuf_loader_area_prepared)
		pixbuf_loader.connect('area_updated', self.on_pixbuf_loader_area_updated)
	
		dotin, dotout = os.popen2([DOT, '-T' + FORMAT], 'rw')

		writer_cb(dotin, *args)
		dotin.close()

		while True:
			buf = dotout.read(8192)
			if not buf:
				break
			pixbuf_loader.write(buf)
			
		dotout.close()
		pixbuf_loader.close()
	
	def set_dotcode(self, dotcode):
		self.write_dotcode(lambda fp: fp.write(dotcode))
	
	def set_graph(self, graph):
		self.write_dotcode(lambda fp: lang.dot.write(graph, fp))
		
	def on_pixbuf_loader_area_prepared(self, pixbuf_loader):
		pixbuf = pixbuf_loader.get_pixbuf()
		self.image.set_from_pixbuf(pixbuf)

	def on_pixbuf_loader_area_updated(self, pixbuf_loader, x, y, width, height):
		self.image.queue_draw()


class DotView(DotWindow, view.View):
	
	def __init__(self, model):
		DotWindow.__init__(self)
		view.View.__init__(self, model)
	
		model.term.attach(self.on_term_update)
		
		if model.term.get() is not None:
			self.on_term_update(model.term)

	def get_name(self, name):
		return 'Inspector View'
		
	def on_term_update(self, term):
		pass

	def on_inspector_window_destroy(self, event):
		self.destroy()
	
	def destroy(self):
		model = self.model

		model.term.detach(self.on_term_update)
		

class CfgView(DotView):

	def on_term_update(self, term):
		term = term.get()
		graph = ir.cfg.render(term)
		self.set_graph(graph)


if __name__ == '__m ain__':
	win = DotWindow()
	win.set_dotcode(sys.stdin.read())
	win.widget.connect('destroy', gtk.main_quit)
	gtk.main()

if __name__ == '__main__':
	import sys 
	import aterm.factory
	
	factory = aterm.factory.Factory()
	term = factory.readFromTextFile(sys.stdin)
	graph = ir.cfg.render(term)
	
	win = DotWindow()
	win.set_graph(graph)
	win.connect('destroy', gtk.main_quit)
	gtk.main()