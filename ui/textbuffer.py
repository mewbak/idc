
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
		self.default_tag = self.buffer.create_tag(None)
		self.highlight_tag = self.default_tag
		
	def write(self, s):
		self.buffer.insert_with_tags(self.iter, s, self.highlight_tag)

	def handle_tag_start(self, name, value):
		if name == 'type':
			self.highlight_tag = self.types.get(value, self.default_tag)

	def handle_tag_end(self, name):
		if name == 'type':
			self.highlight_tag = self.default_tag
