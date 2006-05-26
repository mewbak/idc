'''Visitors used for the implementation of most the term algorithms.

Some of these visitors store no context, therefore are used effectively as
singletons.
'''


from aterm import types
from aterm import visitor


class Comparator(visitor.Visitor):
	'''Base class for term comparators.'''
	
	def visitLit(self, term, other):
		return \
			term.getType() == other.getType() and \
			term.value == other.value

	def visitNil(self, term, other):
		return \
			types.LIST == other.getType() and \
			other.isEmpty()

	def visitCons(self, term, other):
		return \
			types.LIST == other.getType() and \
			not other.isEmpty() and \
			self.visit(term.head, other.head) and \
			self.visit(term.tail, other.tail)

	def visitAppl(self, term, other):
		return \
			types.APPL == other.getType() and \
			self.visit(term.name, other.name) and \
			self.visit(term.args, other.args)		

	def visitWildcard(self, term, other):
		return \
			types.WILDCARD == other.getType()

	def visitVar(self, term, other):
		return \
			types.VAR == other.getType() and \
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


isEquivalent = EquivalenceComparator()


class EqualityComparator(EquivalenceComparator):
	'''Comparator for determining term equality (which contemplates 
	annotations).
	'''

	def visit(self, term, other):
		return \
			EquivalenceComparator.visit(self, term, other) and \
			isEquivalent(term.getAnnotations(), other.getAnnotations())


isEqual = EqualityComparator()


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
			if not PatternComparator([], self.kargs)(term.pattern, other):
				return False
			else:
				self.kargs[name] = other
				return True
		else:
			return isEquivalent(value, other)

	

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


isConstant = Constness()


class Hash(visitor.Visitor):
	'''Perform hashing.'''
	
	# TODO: use a more efficient hash function
	
	def visit(self, term):
		value = visitor.Visitor.visit(self, term)
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
			return hash((value, self.visit(annotations)))
		else:
			return value

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


_getSymbol = _GetSymbol()


class TextWriter(Writer):
	'''Writes a term to a text stream.'''

	def writeAnnotations(self, term):
		annotations = term.getAnnotations()
		if not annotations.isEmpty():
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
		last = tail.getType() == types.LIST and tail.isEmpty()
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
				name.getType() != types.STR \
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
		if pattern.getType() != types.WILDCARD:
			self.fp.write('=')
			self.visit(pattern)


# TODO: implement a XML writer