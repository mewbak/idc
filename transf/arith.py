'''Arithmetic transformations.'''


import aterm

from transf import exception
from transf import combinators


# TODO: complete


class AddInt(combinators.Binary):

	def apply(self, term, context):
		x = self.loperand.apply(term, context)
		y = self.roperand.apply(term, context)
		try:
			return term.factory.makeInt(int(x) + int(y))
		except TypeError:
			raise exception.Failure('not integer terms', x, y)


Add = AddInt


