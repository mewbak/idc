'''List manipulation transformations.

See also U{http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-unstable-latest/manual/chunk-chapter/library-lists.html}.
'''


from transf import exception
from transf import base
from transf import _operate
from transf import match
from transf import build
from transf import project
from transf import unify


length = unify.Count(base.ident)


class _Concat2(_operate.Binary):
	
	def apply(self, term, ctx):
		head = self.loperand.apply(term, ctx)
		tail = self.roperand.apply(term, ctx)
		try:
			return head.extend(tail)
		except AttributeError:
			raise exception.Failure('not term lists', head, tail)

def Concat2(loperand, roperand):
	'''Concatenates two lists.'''
	if loperand is build.nil:
		return roperand
	if roperand is build.nil:
		return loperand
	return _Concat2(loperand, roperand)


def Concat(*operands):
	'''Concatenates several lists.'''
	return _operate.Nary(operands, Concat2, build.nil)

concat = unify.Foldr(build.nil, Concat2)



class Lookup(base.Transformation):
	
	def __init__(self, key, table):
		base.Transformation.__init__(self)
		self.key = key
		self.table = table
	
	def apply(self, term, ctx):
		key = self.key.apply(term, ctx)
		table = self.table.apply(term, ctx)
		
		for name, value in table:
			if key.isEquivalent(name):
				return value
		raise exception.Failure('key not found in table', key, table)
		