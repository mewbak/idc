'''Congruent term transformations.'''


from transf import exception
from transf import base
from transf import variable
from transf import operate
from transf import combine
from transf import match
from transf import _helper


class Cons(match.Cons):
	
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)
		
		new_head = self.head.apply(old_head, ctx)
		new_tail = self.tail.apply(old_tail, ctx)
		
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


class ConsR(Cons):
	
	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)
		
		new_tail = self.tail.apply(old_tail, ctx)
		new_head = self.head.apply(old_head, ctx)
		
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(
				new_head,
				new_tail,
				term.annotations
			)
		else:
			return term


def List(elms, tail = None):
	'''Transformation which traverses a term list. 
	
	@param elms: sequence of transformations to be applied to the elements
	@param tail: option transformation to be applied to the list tail; defaults 
	to matching the empty list
	'''
	if tail is None:
		tail = match.nil
	return operate.Nary(iter(elms), Cons, tail)
	

class Appl(base.Transformation):
	'''Traverse a term application.'''

	def __init__(self, name, args):
		base.Transformation.__init__(self)
		if isinstance(name, basestring):
			self.name = match.Str(name)
		else:
			self.name = name
		if isinstance(args, (tuple, list)):
			self.args = List(args)
		else:
			self.args = args
				
	def apply(self, term, ctx):
		try:
			old_name = term.name
			old_args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)
		
		new_name = self.name.apply(old_name, ctx)
		new_args = self.args.apply(old_args, ctx)
		
		if new_name is not old_name or new_args is not old_args:
			return term.factory.makeAppl(
				new_name,
				new_args,
				term.annotations
			)
		else:
			return term


Var = variable.Traverse


class Annos(base.Transformation):
	
	def __init__(self, annos):
		base.Transformation.__init__(self)
		self.annos = annos

	def apply(self, term, ctx):
		old_annos = term.getAnnotations()
		new_annos = self.annos.apply(old_annos, ctx)
		if new_annos is not old_annos:
			return term.setAnnotations(new_annos)
		else:
			return term


def Anno(anno):
	return Annos(One(anno))


_ = _helper.Factory(match.Int, match.Real, match.Str, List, Appl, Var, match.Pattern)
