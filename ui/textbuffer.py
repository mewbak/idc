
import box


class TextBufferFormatter(box.Formatter):
	'''Formats into a TextBuffer.'''

	# See hypertext.py example included in pygtk distribution

	def __init__(self, buffer):
		box.Formatter.__init__(self)
		
		self.buffer = buffer
		
		self.buffer.set_text("", 0)
		self.iter = self.buffer.get_iter_at_offset(0)
		self.tag = self.buffer.create_tag()
		
	def write(self, s):
		self.buffer.insert_with_tags(self.iter, s, self.tag)

	types = {
		'operator': 'red',
		'keyword': 'blue',
		'symbol': 'black',
		'literal': 'green',
	}
	
	def handle_tag_start(self, name, value):
		if name == 'type':
			try:
				color = self.types[value]
			except KeyError:
				color = 'black'
			self.tag = self.buffer.create_tag(None, foreground=color)

	def handle_tag_end(self, name):
		if name == 'type':
			color = 'black'
			self.tag = self.buffer.create_tag(None, foreground=color)
