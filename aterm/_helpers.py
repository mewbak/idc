'''Visitors used for the implementation of most term algorithms.

Some of these visitors store no context, therefore are used effectively as
singletons.
'''


from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):
	'''Base class for term comparators.'''
	
	def visitLit(self, term, other):
		return \
			term.type == other.type and \
			term.value == other.value

	def visitNil(self, term, other):
		return \
			types.NIL == other.type

	def visitCons(self, term, other):
		return \
			types.CONS == other.type and \
			self.visit(term.head, other.head) and \
			self.visit(term.tail, other.tail)

	def visitAppl(self, term, other):
		if types.APPL != other.type:
			return False
		if term._name != other._name:
			return False
		if len(term._args) != len(other._args):
			return False
		for term_arg, other_arg in zip(term._args, other._args):
			if not self.visit(term_arg, other_arg):
				return False
		return True
	

class EquivalenceComparator(Comparator):
	'''Comparator for determining term equivalence (which does not 
	contemplate annotations).
	'''

	def visit(self, term, other):
		return \
			term is other or \
			Comparator.visit(self, term, other)


isEquivalent = EquivalenceComparator().visit


class EqualityComparator(EquivalenceComparator):
	'''Comparator for determining term equality (which contemplates 
	annotations).
	'''

	def compareAnnos(self, terms, others):
		if terms is None:
			return others is None
		else:
			return others is not None and \
				isEquivalent(terms, others)
		
	def visit(self, term, other):
		return \
			EquivalenceComparator.visit(self, term, other) and \
			self.compareAnnos(term.annotations, other.annotations)


isEqual = EqualityComparator().visit


class Annotator(visitor.Visitor):
	
	def visit(self, term, annotations):
		if term.annotations is annotations:
			return term
		else:
			return visitor.Visitor.visit(self, term, annotations)
		
	def visitInt(self, term, annotations):
		return term.factory.makeInt(term.value, annotations)

	def visitReal(self, term, annotations):
		return term.factory.makeReal(term.value, annotations)
		
	def visitStr(self, term, annotations):
		return term.factory.makeStr(term.value, annotations)
	
	def visitNil(self, term, annotations):
		return term.factory.makeNil(annotations)

	def visitCons(self, term, annotations):
		return term.factory.makeCons(term.head, term.tail, annotations)

	def visitAppl(self, term, annotations):
		return term.factory.makeAppl(term._name, term._args, annotations)

annotate = Annotator().visit


class Remover(visitor.Visitor):
	
	def __init__(self, pattern):
		visitor.Visitor.__init__(self)
		self.pattern = pattern
		
	def visitNil(self, term):
		return term
	
	def visitCons(self, term):
		tail = self.visit(term.tail)
		if term.factory.match(self.pattern, term.head):
			return tail
		elif tail is term.tail:
			return term
		else:
			return term.factory.makeCons(term.head, tail, term.annotations)


class StructuralHash(visitor.Visitor):
	'''Perform hashing without considering.'''
	
	def hash(cls, term):
		return cls().visit(term)
	hash = classmethod(hash)

	# TODO: use a more efficient hash function

	def visitLit(self, term):
		return hash((
			term.type,
			term.value
		))

	def visitNil(self, term):
		return hash((
			term.type,
		))

	def visitCons(self, term):
		return hash((
			term.type,
			self.visit(term.head),
			self.visit(term.tail),
		))

	def visitAppl(self, term):
		return hash((
			term.type,
			term._name,
			term._args,
		))


class Hash(StructuralHash):
	'''Perform hashing.'''
	
	# TODO: use a more efficient hash function
	
	def visit(self, term):
		term_hash = StructuralHash.visit(self, term)
		if term.annotations:
			annos_hash = StructuralHash.hash(term.annotations)
			return hash(term_hash, annos_hash)
		else:
			return term_hash


class Writer(visitor.Visitor):
	'''Base class for term writers.'''
	
	def __init__(self, fp):
		visitor.Visitor.__init__(self)
		self.fp = fp


class _GetSymbol(visitor.Visitor):
	
	def visitStr(self, term):
		return term.value

_getSymbol = _GetSymbol().visit


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
		self.fp.write(term._name)
		args = term.args
		if term._name == '' or term._args:
			self.fp.write('(')
			self.visit(args, inside_list = True)
			self.fp.write(')')
		self.writeAnnotations(term)


class AbbrevTextWriter(TextWriter):
	
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