
import box


class TextBufferFormatter(box.Formatter):
	'''Formats into a TextBuffer.'''

	# See hypertext.py example included in pygtk distribution

	def __init__(self, buffer):
		box.Formatter.__init__(self)
		
		self.buffer = buffer
		
		self.buffer.set_text("", 0)
		self.iter = self.buffer.get_iter_at_offset(0)
		
	def write(self, s):
		self.buffer.insert(self.iter, s)
