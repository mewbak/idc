'''Box viewing.'''


import gtk
import pango

import box
import ir.pprint

from ui.menus import PopupMenu


class TextBufferFormatter(box.Formatter):
	'''Formats into a TextBuffer.'''

	# See hypertext.py example included in pygtk distribution

	def __init__(self, buffer):
		box.Formatter.__init__(self)
		
		self.buffer = buffer
		
		self.buffer.set_text("", 0)
		self.iter = self.buffer.get_iter_at_offset(0)
		
		self.types = {}
		self.types['operator'] = self.buffer.create_tag(None, 
			foreground = 'black'
		)
		self.types['keyword'] = self.buffer.create_tag(None, 
			foreground = 'black', 
			weight=pango.WEIGHT_BOLD
		)
		self.types['literal'] = self.buffer.create_tag(None, 
			foreground = 'dark blue', 
			#foreground = 'green',
			#style=pango.STYLE_ITALIC,
		)
		self.types['symbol'] = self.buffer.create_tag(None,
			foreground = 'dark blue', 
			style=pango.STYLE_ITALIC,
		)
		
		self.default_highlight_tag = self.buffer.create_tag(None)
		self.highlight_tag_stack = [self.default_highlight_tag]
		
		default_path_tag = self.buffer.create_tag(None)
		self.path_tag_stack = [default_path_tag]
		
	def write(self, s):
		highlight_tag = self.highlight_tag_stack[-1]
		path_tag = self.path_tag_stack[-1]
		
		self.buffer.insert_with_tags(self.iter, s, highlight_tag, path_tag)

	def handle_tag_start(self, name, value):
		if name == 'type':
			highlight_tag = self.types.get(value, self.default_highlight_tag)
			self.highlight_tag_stack.append(highlight_tag)
		if name == 'path':
			path_tag = self.buffer.create_tag(None)
			path_tag.set_data('path', value)
			self.path_tag_stack.append(path_tag)

	def handle_tag_end(self, name):
		if name == 'type':
			self.highlight_tag_stack.pop()
		if name == 'path':
			self.path_tag_stack.pop()


class BoxView(gtk.TextView):
	
	def __init__(self, model):
		gtk.TextView.__init__(self)
		self.model = model
		self.model.term.attach(self.on_term_update)
		self.connect("event", self.on_button_press)
		
	def on_term_update(self, term):
		term = term.get()
		boxes = ir.pprint.module(term)
		buffer = self.get_buffer()
		formatter = TextBufferFormatter(buffer)
		writer = box.Writer(formatter)
		writer.write(boxes)

	def on_button_press(self, textview, event):
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

