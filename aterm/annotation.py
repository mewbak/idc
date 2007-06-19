'''Term annotation.'''


from aterm import visitor
from aterm import types
from aterm import lists


def getAll(term):
	'''Get the list of all annotations of this term.'''
	assert term.annotations is not None
	return term.annotations


def setAll(term, annos):
	'''Return a copy of the term with the given annotations.'''
	if not annos:
		annos = None
	if term.type != types.APPL:
		return term
	if term.annotations is annos:
		return term
	else:
		return term.factory.makeAppl(term.name, term.args, annos)


def get(term, label):
	'''Gets an annotation associated with this label.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.type == types.APPL and term.annotations:
		# TODO: avoid the repeated pattern parsing
		anno = lists.fetch(lambda x: term.factory.match(label, x), term.annotations)
		if anno is not None:
			return anno
	raise ValueError("undefined annotation", label)


def set(term, label, anno):
	'''Returns a new version of this term with the
	annotation associated with this label added or updated.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.type != types.APPL:
		return term
	if term.annotations:
		annos = lists.filter(lambda x: not term.factory.match(label, x), term.annotations)
	else:
		annos = term.factory.makeNil()
	annos = term.factory.makeCons(anno, annos)
	return setAll(term, annos)


def remove(term, label):
	'''Returns a copy of this term with the
	annotation associated with this label removed.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if term.type == types.APPL and term.annotations:
		annos = lists.filter(lambda x: not term.factory.match(label, x), term.annotations)
		return setAll(term, annos)
	else:
		return term


def removeAll(term):
	'''Returns a copy of this term with all annotations removed.'''
	return setAll(term, term.factory.makeNil())

