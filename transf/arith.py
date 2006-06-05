'''Arithmetic transformations.'''


import aterm

from transf import exception
from transf import combine
from transf import project


# TODO: complete


class AddInt(combine.Binary):

	def apply(self, term, context):
		x = self.loperand.apply(term, context)
		y = self.roperand.apply(term, context)
		try:
			return term.factory.makeInt(int(x) + int(y))
		except TypeError:
			raise exception.Failure('not integer terms', x, y)


Add = AddInt


add = Add(project.first, project.second)

