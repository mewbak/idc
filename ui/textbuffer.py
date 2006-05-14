
import pango

import box


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
