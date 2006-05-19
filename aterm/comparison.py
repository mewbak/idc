'''Vistors for term comparison.'''


from aterm import types
from aterm import visitor


class EquivalenceComparator(visitor.Visitor):
	'''Comparator for determining structural equivalence.'''

	def __init__(self):
		self.result = True
	
	def compare(self, term, other):
		if term is other:
			return True

		if not self.result:
			return False
		
		term.accept(self, other)
		
		return self.result

	def visitLit(self, term, other):
		self.result = self.result and \
			term.getType() == other.getType() \
			and term.getValue() == other.getValue()
		
	def visitWildcard(self, term, other):
		self.result = self.result and \
			types.WILDCARD == other.getType()

	def visitVar(self, term, other):
		self.result = self.result and \
			types.VAR == other.getType() and \
			term.getName() == other.getName() and \
			self.compare(term.getPattern(), other.getPattern())
	
	def visitNilList(self, term, other):
		self.result = self.result and \
			types.LIST == other.getType() and \
			other.isEmpty()

	def visitConsList(self, term, other):
		self.result = self.result and \
			types.LIST == other.getType() and \
			not other.isEmpty() and \
			self.compare(term.getHead(), other.getHead()) and \
			self.compare(term.getTail(), other.getTail())

	def visitAppl(self, term, other):
		self.result = self.result and \
			types.APPL == other.getType() and \
			self.compare(term.getName(), other.getName()) and \
			self.compare(term.getArgs(), other.getArgs())


class EqualityComparator(EquivalenceComparator):
	'''Comparator for aterm equality (which includes annotations).'''

	def compare(self, term, other):
		EquivalenceComparator.compare(self, term, other)
		
		self.result = self.result and \
			EquivalenceComparator().compare(term.getAnnotations(), other.getAnnotations())

		return self.result


class MatchingComparator(EquivalenceComparator):
	'''Comparator for performing pattern matching.'''

	def __init__(self, args = None, kargs = None):
		EquivalenceComparator.__init__(self)
		
		if args is None:
			self.args = []
		else:
			self.args = args		
		
		if kargs is None:
			self.kargs = {}
		else:
			self.kargs = kargs
		
	def compare(self, term, other):
		if not self.result:
			return False
		
		term.accept(self, other)
		return self.result
	
	def visitWildcard(self, term, other):
		self.args.append(other)

	def visitVar(self, term, other):
		name = term.getName()
		try:
			value = self.kargs[name]
			if not EquivalenceComparator().compare(self.kargs[name], other):
				self.result = False
		except KeyError:
			if not MatchingComparator([], self.kargs).compare(term.getPattern(), other):
				self.result = False
			self.kargs[name] = other
			return True
	

	
	