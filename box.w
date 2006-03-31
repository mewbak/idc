'''Pretty-printing of aterm code using boxes as an intermediate representation,
allowing to easily support several frontend languages and backend formats.

See
http://www.cs.uu.nl/wiki/Visser/GenerationOfFormattersForContext-freeLanguages
about the Box language, upon this code is lossely based.
'''

header {
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import aterm
import walker
}


class Box2Text:
	'''Convert box terms into ASCII text.'''

	{
	def __init__(self, factory, fp):
		Walker.__init__(self, factory)
		self._fp = fp
		self._indent = 0
	
	def write(self, s):
		self._fp.write(s)
	
	def indent(self):
		self._indent += 1
	
	def dedent(self):
		self._indent -= 1
		assert self._indent >= 0

	def write_indent(self):
		self._fp.write('\t'*self._indent)
	
	def write_eol(self):
		self._fp.write('\n')
	
	}
	
	write_box
		: H(bl:_list)
			{
				for b in $bl:
					self.write_box(b) 
			}
		| V(bl:_list)
			{
				for b in $bl:
					self.write_vbox(b) 
			}
		| I(b)
			{
				sys.stderr.write("warning: indent outside vbox: %r\n" % $<)
				self.write_box($b)
			}
		| s:_str
			{
				self.write($s.getValue())
			}
		;

	write_vbox
		: I(b)
			{
				self.indent()
				self.write_vbox($b)
				self.dedent()
			}
		| b
			{
				self.write_indent()
				self.write_box($b)
				self.write_eol()
			}
		;

header {
def box2text(boxes):
	'''Convert box terms into a string.'''

	fp = StringIO()
	writer = Box2Text(boxes.factory, fp)
	writer.write_box(boxes)
	return fp.getvalue()
}

class Term2Box:

	# XXX: incomplete

	depth
		: f(*a)
			{ return 1 + self.depth($a) }
		| []
			{ return 0 }
		| [h,*t]
			{ return max(self.depth($h), self.depth($t)) }
		| _
			{ return 0 }
		;
		
	convert
		: f(*a) -> H([f, "(", :convert_list(a), ")"], 0)
		| [] -> H(["[", "]"], 0)
		| [h,*t] -> H(["[", "]"], 0)
		| _
			{ $$ = self.factory.make("_", repr($<.getValue())) }
		;
	
	convert_list
		: [] -> []
		| [h, *t] -> [:convert(h), *:convert_list(t)]
		;
	
	
header {
def term2box(term):
	'''Convert an aterm into its box representation.'''

	boxer = Term2Box(term.getFactory())
	box = boxer.convert(term)
	return box
}

# vim:set syntax=python:
