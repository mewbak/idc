'''Pretty-printing of aterm code using boxes as an intermediate representation,
allowing to easily support several frontend languages and backend formats.

See
http://www.cs.uu.nl/wiki/Visser/GenerationOfFormattersForContext-freeLanguages
about the Box language, upon this code is lossely based.
'''

import sys

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import aterm.types
from aterm import walker
import transf


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

	def write_indent(self):
		'''Write the indentation characters.'''
		if self.indent_level > 0:
			self.write('\t'*self.indent_level)
	
	def write_eol(self):
		'''Write the end-of-line character.'''
		self.write('\n')
	
	def handle_tag_start(self, name, value):
		'''Handle the start of a tag. Tags can be used for describing token types, 
		or the originating term path.'''
		pass

	def handle_tag_end(self, name):
		'''Handle the end of a tag.'''
		pass


class TextFormatter(Formatter):
	'''Formatter for plain-text files.'''

	def __init__(self, fp):
		Formatter.__init__(self)
		self.fp = fp
	
	def write(self, s):
		self.fp.write(s)


class AnsiTextFormatter(TextFormatter):
	'''Formatter for plain-text files which outputs ANSI escape codes. See 
	http://en.wikipedia.org/wiki/ANSI_escape_code for more information 
	concerning ANSI escape codes.
	'''

	csi = '\33['
	
	types = {
		'operator': '31m', # red
		'keyword': '1m', # bold
		'symbol': '34m', # blue
		'literal': '32m', # green
	}
	
	def handle_tag_start(self, name, value):
		if name == 'type':
			try:
				code = self.types[value] 
			except KeyError:
				code = '0m'
			self.write(self.csi + code)

	def handle_tag_end(self, name):
		if name == 'type':
			self.write(self.csi + '0m')


class Writer(walker.Walker):
	'''Writes boxes trhough a formatter.'''

	NONE, VERT, HORIZ = range(3)
	
	def __init__(self, formatter):
		walker.Walker.__init__(self)
		self.formatter = formatter
	
	def write(self, box, mode = NONE):
		self._write(box, mode = mode)
	
	_write = walker.Dispatch('write')
	
	def writeV(self, boxes, mode):
		if mode == self.HORIZ:
			raise Warning('vbox inside hbox', boxes)
		else:
			mode = self.VERT
		for box in boxes:
			self.write(box, mode)
	
	def writeI(self, box, mode):
		self.formatter.indent()
		self.write(box, mode)
		self.formatter.dedent()
	
	def writeD(self, box, mode):
		self.formatter.dedent()
		self.write(box, mode)
		self.formatter.indent()
	
	def writeT(self, name, value, box, mode):
		name = self._str(name)
		try:
			value = self._str(value)
		except TypeError:
			pass
		self.formatter.handle_tag_start(name, value)
		self.write(box, mode)
		self.formatter.handle_tag_end(name)

	def writeH(self, boxes, mode):
		if mode == self.VERT:
			self.formatter.write_indent()
		for box in boxes:
			self.write(box, mode = self.HORIZ)
		if mode == self.VERT:
			self.formatter.write_eol()
	
	def write_Str(self, s, mode):
		if mode == self.VERT:
			self.formatter.write_indent()
		self.formatter.write(s)
		if mode == self.VERT:
			self.formatter.write_eol()


def write(boxes, formatter):
	'''Write the boxes with an formatter.'''
	writer = Writer(formatter)
	writer.write(boxes)


def stringify(boxes, Formatter = TextFormatter):
	'''Convert box terms into a string.'''
	fp = StringIO()
	write(boxes, Formatter(fp))
	return fp.getvalue()


def Tag(name, value, operand = None):
	if isinstance(name, basestring):
		name = transf.build.Str(name)
	if isinstance(value, basestring):
		value = transf.build.Str(value)
	if operand is None:
		operand = transf.base.ident
	return transf.build.Appl('T', (name, value, operand))

op = Tag('type', 'operator')
kw = Tag('type', 'keyword')
const = Tag('type', 'constant')
string = Tag('type', 'string')
sym = Tag('type', 'symbol')

def Path(operand):
	return Tag('path', transf.path.get, operand ) + operand

def reprz(term):
	return term.factory.makeStr(str(term))
reprz = transf.util.Adaptor(reprz)

def escape(term):
	s = str(term.value)
	s = s.replace('\"', '\\"')
	s = s.replace('\t', '\\t')
	s = s.replace('\r', '\\r')
	s = s.replace('\n', '\\n')
	s = '"' + s + '"'
	return term.factory.makeStr(s)
escape = transf.util.Adaptor(escape)

class Lit(transf.base.Transformation):
	def apply(self, term, ctx):
		if term.type == aterm.types.INT:
			term = term.factory.makeStr(str(term.value))
			return const.apply(term, ctx)
		if term.type == aterm.types.REAL:
			term = term.factory.makeStr(str(term.value))
			return const.apply(term, ctx)
		if term.type == aterm.types.STR:
			term = escape.apply(term, ctx)
			return string.apply(term, ctx)
		raise transf.exception.Failure
lit = Lit()


def Prefix(sep):
	return transf.unify.Foldr(
		transf.base.ident,
		lambda head, tail: transf.build.List([sep, head], tail=tail)
	)


def Join(sep):
	return \
		transf.match.nil + \
		transf.congruent.Cons(
			transf.base.ident,
			Prefix(sep)
		)

def HBox(boxes):
	return transf.build.Appl('H', (boxes,))

commas = HBox(Join(transf.build.Str(', ')))
spaces = HBox(Join(transf.build.Str(' ')))
