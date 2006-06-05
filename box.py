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
import walker
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
	
	def __init__(self, factory, formatter):
		walker.Walker.__init__(self, factory)
		self.formatter = formatter
	
	def write(self, box, mode = NONE):
		if box.type == aterm.types.APPL:
			self._dispatchAppl(box, "write", mode = mode)
		elif box.type == aterm.types.STR:
			self.writeS(box, mode)
		else:
			raise ValueError('bad box', box)
	
	def writeV(self, boxes, mode):
		if mode == self.HORIZ:
			sys.stderr.write("warning: vbox inside hbox: %r\n" % boxes)
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
	
	def writeT(self, n, v, box, mode):
		assert n.type == aterm.types.STR
		assert v.type == aterm.types.STR
		self.formatter.handle_tag_start(n.value, v.value)
		self.write(box, mode)
		self.formatter.handle_tag_end(n.value)

	def writeH(self, boxes, mode):
		if mode == self.VERT:
			self.formatter.write_indent()
		for box in boxes:
			self.write(box, mode = self.HORIZ)
		if mode == self.VERT:
			self.formatter.write_eol()
	
	def writeS(self, s, mode):
		if mode == self.VERT:
			self.formatter.write_indent()
		self.formatter.write(s.value)
		if mode == self.VERT:
			self.formatter.write_eol()


def box2text(boxes, formatterClass = TextFormatter):
	'''Convert box terms into a string.'''

	fp = StringIO()
	formatter = formatterClass(fp)
	writer = Writer(boxes.factory, formatter)
	writer.write(boxes)
	return fp.getvalue()


def Tag(name, value, operand = None):
	if operand is None:
		operand = transf.base.Ident()
	return transf.build.BuildAppl(
		'T',
		 [
			transf.build.BuildStr(name),
			transf.build.BuildStr(value),
			operand,
		]
	)

op = Tag('type', 'operator')
kw = Tag('type', 'keyword')
const = Tag('type', 'constant')
string = Tag('type', 'string')
sym = Tag('type', 'symbol')


def escape(term, context):
	s = str(term.value)
	s = s.replace('\"', '\\"')
	s = s.replace('\t', '\\t')
	s = s.replace('\r', '\\r')
	s = s.replace('\n', '\\n')
	s = '"' + s + '"'
	return term.factory.makeStr(s)
escape = transf.base.Adaptor(escape)


def lit(term, context):
	if term.type == aterm.types.INT:
		term = term.factory.makeStr(str(term.value))
		return const.apply(term, context)
	if term.type == aterm.types.REAL:
		term = term.factory.makeStr(str(term.value))
		return const.apply(term, context)
	if term.type == aterm.types.STR:
		term = escape.apply(term, context)
		return string.apply(term, context)
lit = transf.base.Adaptor(lit)


def Prefix(sep):
	prefix = transf.base.Proxy()
	prefix.subject \
		= transf.match.MatchNil() \
		| transf.build.BuildCons(
			sep,
			transf.build.BuildCons(
				transf.project.Head(),
				transf.project.Tail() & prefix
			)
		)
	return prefix

def Join(sep):
	return \
		transf.match.MatchNil() \
		| transf.traverse.TraverseCons(
			transf.base.Ident(),
			Prefix(sep)
		)
	
commas \
	= transf.build.BuildAppl(
		'H', 
		[Join(transf.build.BuildStr(', '))]
	)
