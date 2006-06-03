'''List manipulation transformations.'''


from transf import exception
from transf import base
from transf import combinators


class Concat(combinators.Binary):
	
	def apply(self, term, context):
		head = self.loperand.apply(term, context)
		tail = self.roperand.apply(term, context)
		try:
			return head.extend(tail)
		except AttributeError:
			raise exception.Failure('not term lists', head, tail)