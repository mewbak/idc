'''Term building transformations.'''


import aterm.factory
import aterm.types

from transf import base
from transf import exception


_factory = aterm.factory.Factory()


class BuildTerm(base.Transformation):

	def __init__(self, term):
		base.Transformation.__init__(self)
		self.term = term
	
	def apply(self, term, context):
		return self.term


def BuildInt(value):
	term = _factory.makeInt(value)
	return BuildTerm(term)


def BuildReal(value):
	term = _factory.makeReal(value)
	return BuildTerm(term)


def BuildStr(value):
	term = _factory.makeStr(value)
	return BuildTerm(term)


def BuildNil():
	term = _factory.makeNil()
	return BuildTerm(term)


class BuildCons(base.Transformation):
	
	def __init__(self, head, tail):
		base.Transformation.__init__(self)
		self.head = head
		self.tail = tail
		
	def apply(self, term, context):
		head = self.head.apply(term, context)
		tail = self.tail.apply(term, context)
		return term.factory.makeCons(head, tail)


def _BuildList(elms_iter, tail):
	try:
		elm = elms_iter.next()
	except StopIteration:
		return tail
	else:
		return BuildCons(elm, _BuildList(elms_iter, tail))


def BuildList(elms, tail = None):
	if tail is None:
		tail = BuildNil()
	return _BuildList(iter(elms), tail)
	

class BuildAppl(base.Transformation):
	
	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = BuildStr(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = BuildList(args)
		else:
			self.args = args
		
	def apply(self, term, context):
		name = self.name.apply(term, context)
		args = self.args.apply(term, context)
		return term.factory.makeAppl(name, args)


class BuildVar(base.Transformation):
	
	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name
	
	def apply(self, term, context):
		try:
			return context[self.name]
		except KeyError:
			raise exception.Failure('undefined variable', self.name)


class BuildPattern(base.Transformation):

	def __init__(self, pattern):
		base.Transformation.__init__(self)
		if isinstance(pattern, basestring):
			self.pattern = _factory.parse(pattern)
		else:
			self.pattern = pattern
	
	def apply(self, term, context):
		# FIXME: avoid the dict copy
		return self.pattern.make(term, **dict(context))
