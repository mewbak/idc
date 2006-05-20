'''Visitors for term writing.'''


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
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			self.fp.write('{')
			self.visit(annotations, inside_list = True)
			self.fp.write('}')

	def visitInt(self, term):
		self.fp.write(str(term.getValue()))
		self.writeAnnotations(term)
	
	def visitReal(self, term):
		self.fp.write('%g' % term.getValue())
		self.writeAnnotations(term)
	
	def visitStr(self, term):
		s = str(term.getValue())
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
		head = term.getHead()
		self.visit(head)
		tail = term.getTail()
		last = tail.getType() == types.LIST and tail.isEmpty()
		if not last:
			self.fp.write(",")
			self.visit(tail, inside_list = True)		
		if not inside_list:
			self.fp.write(']')
			self.writeAnnotations(term)

	def visitAppl(self, term):
		name = term.getName()
		# TODO: verify strings
		self.fp.write(name.getSymbol())
		args = term.getArgs()
		if \
				name.getType() != types.STR \
				or name.getValue() == '' \
				or not args.isEquivalent(args.factory.makeNil()):
			self.fp.write('(')
			self.visit(args, inside_list = True)
			self.fp.write(')')
		self.writeAnnotations(term)

	def visitVar(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		self.fp.write(str(term.getName()))
		pattern = term.getPattern()
		if pattern.getType() != types.WILDCARD:
			self.fp.write('=')
			self.visit(pattern)
		
	def visitWildcard(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		else:
			self.fp.write('_')


# TODO: implement a XML writer