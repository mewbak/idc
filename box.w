'''Pretty-printing of aterm code using boxes as an intermediate representation,
allowing to easily support several frontend languages and backend formats.

See
http://www.cs.uu.nl/wiki/Visser/GenerationOfFormattersForContext-freeLanguages
about the Box language, upon this code is lossely based.
'''

header {
import sys

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import aterm
import walker


class Formatter:
	'''Base class for output formatters.'''

	def __init__(self):
		self.indent_level = 0
	
	def write(self, s):
		'''Write text.'''
		raise NotImplementedError
	
	def indent(self):
		'''Increase the indentation level.'''
		self.indent_level += 1
	
	def dedent(self):
		'''Decrease the indentation level.'''
		self.indent_level -= 1
		assert self.indent_level >= 0

	def write_indent(self):
		'''Write the indentation characters.'''
		self.write('\t'*self.indent_level)
	
	def write_eol(self):
		'''Write the end-of-line character.'''
		self.write('\n')
	
	def handle_tag_start(self, name, value):
		''''''
		pass

	def handle_tag_end(self, name):
		pass


class TextFormatter(Formatter):
	'''Formatter for plain-text files.'''

	def __init__(self, fp):
		Formatter.__init__(self)
		self.fp = fp
	
	def write(self, s):
		self.fp.write(s)

}


class Writer:
	'''Writes boxes trhough a formatter.'''

	{
	def __init__(self, factory, formatter):
		Walker.__init__(self, factory)
		self.formatter = formatter
	}
	
	write_box
		: s:_str # string literal
			{
				self.formatter.write($s.getValue())
			}
		| H(bl:_list) # horizontal stack
			{
				for b in $bl:
					self.write_box(b) 
			}
		| V(bl:_list) # vertical stack
			{
				for b in $bl:
					self.write_vbox(b) 
			}
		| I(b) # indent
			{
				sys.stderr.write("warning: indent outside vbox: %r\n" % $<)
				self.write_box($b)
			}
		| D(b) # dedent
			{
				sys.stderr.write("warning: dedent outside vbox: %r\n" % $<)
				self.write_box($b)
			}
		| T(n:_str, v:_str, b) # tag
			{
				self.formatter.handle_start_tag(
				self.write_box($b)
			}
		| :_fatal("bad box")
		;

	write_vbox
		: I(b)
			{
				self.formatter.indent()
				self.write_vbox($b)
				self.formatter.dedent()
			}
		| D(b)
			{
				self.formatter.dedent()
				self.write_vbox($b)
				self.formatter.indent()
			}
		| V(bl:_list)
			{
				for b in $bl:
					self.write_vbox(b) 
			}
		| b
			{
				self.formatter.write_indent()
				self.write_box($b)
				self.formatter.write_eol()
			}
		| :_fatal("bad box")
		;


header {
def box2text(boxes):
	'''Convert box terms into a string.'''

	fp = StringIO()
	formatter = TextFormatter(fp)
	writer = Writer(boxes.factory, formatter)
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
