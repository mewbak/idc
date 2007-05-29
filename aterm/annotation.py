'''Term annotation.'''


from aterm import visitor


def getAll(term):
	'''Get the list of all annotations of this term.'''
	if term.annotations is None:
		return term.factory.makeNil()
	else:
		return term.annotations


class _Setter(visitor.Visitor):

	def __init__(self, annos):
		visitor.Visitor.__init__(self)
		self.annos = annos

	def visitTerm(self, term):
		assert False

	def visitInt(self, term):
		return term.factory.makeInt(term.value, self.annos)

	def visitReal(self, term):
		return term.factory.makeReal(term.value, self.annos)

	def visitStr(self, term):
		return term.factory.makeStr(term.value, self.annos)

	def visitNil(self, term):
		return term.factory.makeNil(self.annos)

	def visitCons(self, term):
		return term.factory.makeCons(term.head, term.tail, self.annos)

	def visitAppl(self, term):
		return term.factory.makeAppl(term.name, term.args, self.annos)

def setAll(term, annos):
	'''Return a copy of the term with the given annotations.'''
	if not annos:
		annos = None
	if term.annotations is annos:
		return term
	else:
		annotator = _Setter(annos)
		return term.accept(annotator)


class _Getter(visitor.Visitor):

	def __init__(self, pattern):
		visitor.Visitor.__init__(self)
		self.pattern = pattern

	def visitTerm(self, term):
		assert False

	def visitNil(self, term):
		return None

	def visitCons(self, term):
		# TODO: avoid the repeated pattern parsing
		if term.factory.match(self.pattern, term.head):
			return term.head
		else:
			return self.visit(term.tail)

def get(term, label):
	'''Gets an annotation associated with this label.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.annotations:
		getter = _Getter(label)
		anno = term.annotations.accept(getter)
		if anno is not None:
			return anno
	raise ValueError("undefined annotation", label)


def set(term, label, anno):
	'''Returns a new version of this term with the
	annotation associated with this label added or updated.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.annotations:
		remover = _Remover(label)
		annos = term.annotations.accept(remover)
	else:
		annos = term.factory.makeNil()
	annos = term.factory.makeCons(anno, annos)
	return setAll(term, annos)


class _Remover(visitor.Visitor):

	def __init__(self, pattern):
		visitor.Visitor.__init__(self)
		self.pattern = pattern

	def visitTerm(self, term):
		assert False

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


def remove(term, label):
	'''Returns a copy of this term with the
	annotation associated with this label removed.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.annotations:
		remover = _Remover(label)
		annos = term.annotations.accept(remover)
		return setAll(term, annos)
	else:
		return term


def removeAll(term):
	'''Returns a copy of this term with all annotations removed.'''
	return setAll(term, None)

