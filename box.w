# Pretty-printing using boxes
#
# See:
#   http://www.cs.uu.nl/wiki/Visser/GenerationOfFormattersForContext-freeLanguages

header {
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

import aterm
import walker
}


class Box2Text:

	{
	def __init__(self, factory, fp):
		Walker.__init__(self, factory)
		self._fp = fp
		self._indent = 0
	
	def write(self, s):
		self._fp.write(s)
	
	def indent(self, i):
		self._indent += i
	
	def deindent(self, i):
		self._indent -= i
		assert self._indent >= 0

	def write_indent(self):
		self._fp.write('\t'*self._indent)
	
	def write_eol(self):
		self._fp.write('\n')
	
	}
	
	write_box
		: H(b, hs)
			{
				import sys
				sys.stderr.write(repr($b) + '\n')
				sys.stderr.write(repr($hs) + '\n')
				sys.stderr.write(repr($hs.getValue()) + '\n')
				sep = ' '*$hs.getValue()
				first = True
				for box in $b:
					if first:
						first = False
					else:
						self.write(sep)
					self.write_box(box) 
			}
		| V(b, vs, is)
			{
				self.indent($is.getValue())
				for box in $b:
					self.write_indent()
					self.write_box(box) 
					for i in range($vs.getValue()):
						self.write_eol()
				self.deindent($is.getValue())
			}
		| S(s)
			{
				self.write($s.getValue())
			}
		;

header {
def box2text(boxes):
	fp = StringIO()
	writer = Box2Text(boxes.factory, fp)
	writer.write_box(boxes)
	return fp.getvalue()
}

class Aterm2Box:

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
		: f(*a) -> H([f, S("("), .convert_list(a), S(")")], 0)
		| [] -> H([S("["), S("]")], 0)
		| [h,*t] -> H([S("["), S("]")], 0)
		| _
			{ $$ = self.factory.make("S(_)", repr($<.getValue())) }
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
		: Module(stmts) -> V(.map(stmts, {self.stmt}), 1, 0)
		;
	
	stmt
		: Label(name) -> H([S(name),S(":")], 0)
		| Assembly(opcode, operands) -> H([S("asm"),S("("), .string(opcode), S(")")], 0)
		;
	
	string
		: _ -> H([S("\""), S(_), S("\"")], 0)
		;

header {
def c2box(term):
	boxer = C2Box(term.getFactory())
	box = boxer.convert(term)
	return box
}
