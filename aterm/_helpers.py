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
			types.LIST == other.type and \
			other.isEmpty()

	def visitCons(self, term, other):
		return \
			types.LIST == other.type and \
			not other.isEmpty() and \
			self.visit(term.head, other.head) and \
			self.visit(term.tail, other.tail)

	def visitAppl(self, term, other):
		return \
			types.APPL == other.type and \
			self.visit(term.name, other.name) and \
			self.visit(term.args, other.args)		

	def visitWildcard(self, term, other):
		return \
			types.WILDCARD == other.type

	def visitVar(self, term, other):
		return \
			types.VAR == other.type and \
			term.name == other.name and \
			self.visit(term.pattern, other.pattern)
	

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


class PatternComparator(Comparator):
	'''Comparator for performing pattern matching.'''

	def __init__(self, args = None, kargs = None):
		Comparator.__init__(self)
		
		if args is None:
			self.args = []
		else:
			self.args = args		
		
		if kargs is None:
			self.kargs = {}
		else:
			self.kargs = kargs
	
	def visitLit(self, term, other):
		return \
			term is other or \
			Comparator.visitLit(self, term, other)
	
	def visitWildcard(self, term, other):
		self.args.append(other)
		return True

	def visitVar(self, term, other):
		name = term.name
		try:
			value = self.kargs[name]
		except KeyError:
			if not PatternComparator([], self.kargs).visit(term.pattern, other):
				return False
			else:
				self.kargs[name] = other
				return True
		else:
			return isEquivalent(value, other)


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
		return term.factory.makeAppl(term.name, term.args, annotations)

	def visitWildcard(self, term, annotations):
		return term.factory.makeWildcard(annotations)
		
	def visitVar(self, term, annotations):
		return term.factory.makeVar(term.name, term.pattern, annotations)

annotate = Annotator().visit


class Remover(visitor.Visitor):
	
	def __init__(self, pattern):
		visitor.Visitor.__init__(self)
		self.pattern = pattern
		
	def visitNil(self, term):
		return term
	
	def visitCons(self, term):
		tail = self.visit(term.tail)
		if self.pattern.match(term.head):
			return tail
		elif tail is term.tail:
			return term
		else:
			return term.factory.makeCons(term.head, tail, term.annotations)


class Maker(visitor.IncrementalVisitor):
	
	def __init__(self, args, kargs):
		self.args = list(args)
		self.kargs = kargs
	
	def visitLit(self, term):
		return term
	
	def visitNil(self, term):
		return term
	
	def visitHead(self, term):
		return self.visit(term)
	
	def visitTail(self, term):
		return self.visit(term)
		
	def visitName(self, term):
		return self.visit(term)
	
	def visitArgs(self, term):
		return self.visit(term)
	
	def visitWildcard(self, term):
		try:
			return self.args.pop(0)
		except IndexError:
			raise TypeError('insufficient number of arguments')
			
	def visitVar(self, term):
		try:
			# TODO: do something with the pattern here?
			return self.kargs[term.name]
		except KeyError:
			raise ValueError('undefined term variable %s' % term.name)
	

class Constness(visitor.Visitor):
	'''Visitor for determining if a term is constant.'''
	
	def visitLit(self, term):
		return True

	def visitNil(self, term):
		return True

	def visitCons(self, term):
		return \
			self.visit(term.head) and \
			self.visit(term.tail)

	def visitAppl(self, term):
		return \
			self.visit(term.name) and \
			self.visit(term.args)		

	def visitPlaceholder(self, term):
		return False

isConstant = Constness().visit


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
			self.visit(term.name),
			self.visit(term.args),
		))

	def visitWildcard(self, term):
		return hash((
			term.type,
		))

	def visitVar(self, term):
		return hash((
			term.type,
			term.name,
			self.visit(term.pattern),
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

	def visitLit(self, term):
		return hash(term.value)

	def visitNil(self, term):
		return hash(())

	def visitCons(self, term):
		return hash((
			self.visit(term.head),
			self.visit(term.tail),
		))

	def visitAppl(self, term):
		return hash((
			self.visit(term.name),
			self.visit(term.args),
		))

	def visitWildcard(self, term):
		return hash(None)

	def visitVar(self, term):
		return hash((
			term.name,
			self.visit(term.pattern),
		))


class Writer(visitor.Visitor):
	'''Base class for term writers.'''
	
	def __init__(self, fp):
		visitor.Visitor.__init__(self)
		self.fp = fp


class _GetSymbol(visitor.Visitor):
	
	def visitStr(self, term):
		return term.value

	def visitWildcard(self, term):
		return '_'
	
	def visitVar(self, term):
		return term.name

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
		self.fp.write('%g' % term.value)
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
		last = tail.type == types.LIST and tail.isEmpty()
		if not last:
			self.fp.write(",")
			self.visit(tail, inside_list = True)		
		if not inside_list:
			self.fp.write(']')
			self.writeAnnotations(term)

	def visitAppl(self, term):
		name = term.name
		self.fp.write(_getSymbol(name))
		args = term.args
		if \
				name.type != types.STR \
				or name.value == '' \
				or not args.isEquivalent(args.factory.makeNil()):
			self.fp.write('(')
			self.visit(args, inside_list = True)
			self.fp.write(')')
		self.writeAnnotations(term)
		
	def visitWildcard(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		else:
			self.fp.write('_')
			
	def visitVar(self, term, inside_list = False):
		if inside_list:
			self.fp.write('*')
		self.fp.write(str(term.name))
		pattern = term.pattern
		if pattern.type != types.WILDCARD:
			self.fp.write('=')
			self.visit(pattern)


# TODO: implement a XML writer