'''Term building transformations.'''


import aterm.types

from transf import base
from transf import exception


# TODO: handle annotations


class _BuildLit(base.Transformation):

	def __init__(self, value):
		base.Transformation.__init__(self)
		self.value = value


class BuildInt(_BuildLit):
	
	def apply(self, term, context):
		return term.factory.makeInt(self.value)


class BuildReal(_BuildLit):
	
	def apply(self, term, context):
		return term.factory.makeReal(self.value)


class BuildStr(_BuildLit):
	
	def apply(self, term, context):
		return term.factory.makeStr(self.value)


class BuildNil(base.Transformation):
	
	def apply(self, term, context):
		return term.factory.makeNil()


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


def BuildList(elms):
	return _BuildList(iter(elms), BuildNil())
	

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
