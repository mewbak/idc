'''String manipulation transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import combine


class ToStr(base.Transformation):
	
	def apply(self, term, ctx):
		try:
			return term.factory.makeStr(str(term.value))
		except AttributeError:
			raise exception.Failure('not a literal term', term)

