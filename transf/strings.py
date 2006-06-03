'''String manipulation transformations.'''


import aterm.types

from transf import exception
from transf import base
from transf import combinators


class ToStr(base.Transformation):
	
	def apply(self, term, context):
		if term.type not in (aterm.types.INT, aterm.types.REAL, aterm.types.STR):
			raise exception.Failure('not a literal term', term)
		return term.factory.makeStr(str(term.value))

