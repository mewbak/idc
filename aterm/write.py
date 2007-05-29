'''Term writing.'''


from aterm import types
from aterm import visitor


class Writer(visitor.Visitor):
	'''Base class for term writers.'''

	def __init__(self, fp):
		visitor.Visitor.__init__(self)
		self.fp = fp


class TextWriter(Writer):
	'''Writes a term to a text stream.'''

	def writeAnnotations(self, term):
		annotations = term.annotations
		if annotations:
			self.fp.write('{')
			self.visit(annotations, inside_list = True)
			self.fp.write('}')

	def visitInt(self, term):
		self.fp.write(str(term.value))
		self.writeAnnotations(term)

	def visitReal(self, term):
		value = term.value
		if float(int(value)) == value:
			self.fp.write('%0.1f' % value)
		else:
			self.fp.write('%g' % value)
		self.writeAnnotations(term)

	def visitStr(self, term):
		s = str(term.value)
		s = s.replace('\"', '\\"')
		s = s.replace('\t', '\\t')
		s = s.replace('\r', '\\r')
		s = s.replace('\n', '\\n')
		self.fp.write('"' + s + '"')
		self.writeAnnotations(term)

	def visitNil(self, term, inside_list = False):
		if not inside_list:
			self.fp.write('[]')
			self.writeAnnotations(term)

	def visitCons(self, term, inside_list = False):
		if not inside_list:
			self.fp.write('[')
		head = term.head
		self.visit(head)
		tail = term.tail
		last = tail.type == types.NIL
		if not last:
			self.fp.write(",")
			self.visit(tail, inside_list = True)
		if not inside_list:
			self.fp.write(']')
			self.writeAnnotations(term)

	def visitAppl(self, term):
		self.fp.write(term.name)
		args = term.args
		if term.name == '' or term.args:
			self.fp.write('(')
			sep = ""
			for arg in term.args:
				self.fp.write(sep)
				self.visit(arg)
				sep = ","
			self.fp.write(')')
		self.writeAnnotations(term)


class AbbrevTextWriter(TextWriter):
	'''Write an abbreviated term representation.'''

	def __init__(self, fp, depth):
		super(AbbrevTextWriter, self).__init__(fp)
		self.depth = depth

	def visitCons(self, term, inside_list = False):
		if not inside_list:
			self.fp.write('[')

		if self.depth > 1:
			self.depth -= 1
			head = term.head
			self.visit(head)
			self.depth += 1
			tail = term.tail
			last = tail.type == types.NIL
			if not last:
				self.fp.write(",")
				self.visit(tail, inside_list = True)
		else:
			self.fp.write('...')

		if not inside_list:
			self.fp.write(']')
			self.writeAnnotations(term)


# TODO: implement a XML writer