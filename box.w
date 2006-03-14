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
	
	def indent(self, i):
		self._indent += i
	
	def dedent(self, i):
		self._indent -= i
		assert self._indent >= 0

	def write_indent(self):
		self._fp.write('\t'*self._indent)
	
	def write_eol(self):
		self._fp.write('\n')
	
	}
	
	write_box
		: H(bl, hs)
			{
				if $bl.getType() != aterm.LIST:
					raise Failure
				if $hs.getType() != aterm.INT:
					raise Failure
				sep = ' '*$hs.getValue()
				first = True
				for b in $bl:
					if first:
						first = False
					else:
						self.write(sep)
					self.write_box(b) 
			}
		| V(bl, vs)
			{
				if $bl.getType() != aterm.LIST:
					raise Failure
				if $vs.getType() != aterm.INT:
					raise Failure
				for b in $bl:
					self.write_vbox(b, $vs.getValue()) 
			}
		| I(b, is)
			{
				sys.stderr.write("warning: indent outside vbox: %r\n" % $<)
				self.write_box($b)
			}
		| s
			{
				if $s.getType() != aterm.STR:
					raise Failure
				self.write($s.getValue())
			}
		| _
			{
				import sys
				sys.stderr.write("error: bad box: %r\n" % $<)
				raise Failure
			}
			
		;

	write_vbox({vs})
		: I(b, is)
			{
				if $is.getType() != aterm.INT:
					raise Failure
				self.indent($is.getValue())
				self.write_vbox($b, vs)
				self.dedent($is.getValue())
			}
		| b
			{
				self.write_indent()
				self.write_box($b)
				for i in range(vs):
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

class Aterm2Box:

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
		: f(*a) -> H([f, "(", .convert_list(a), ")"], 0)
		| [] -> H(["[", "]"], 0)
		| [h,*t] -> H(["[", "]"], 0)
		| _
			{ $$ = self.factory.make("_", repr($<.getValue())) }
		;
	
	convert_list
		: [] -> []
		| [h, *t] -> [.convert(h), * .convert_list(t)]
		;
	
	
class C2Box:

	convert
		: .module
		| .stmt
		;
	
	module
		: Module(stmts) -> V(.map(stmts, {self.stmt}), 1)
		;
	
	stmt
		: Label(name) -> H([name,":"], 0)
		| Assembly(opcode, operands) -> H(["asm","(", .string(opcode), ")"], 0)
		;
	
	string
		: _ -> H(["\"", _, "\""], 0)
		;

header {
def c2box(term):
	'''Convert an aterm containg C code into its box representation.'''

	boxer = C2Box(term.getFactory())
	box = boxer.convert(term)
	return box
}
