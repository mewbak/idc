'''List manipulation transformations.

See also U{http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-unstable-latest/manual/chunk-chapter/library-lists.html}.
'''


from transf import exception
from transf import base
from transf import combine
from transf import match
from transf import build
from transf import project
from transf import unify


length = unify.Count(base.ident)


class _Concat(combine.Binary):
	
	def apply(self, term, context):
		head = self.loperand.apply(term, context)
		tail = self.roperand.apply(term, context)
		try:
			return head.extend(tail)
		except AttributeError:
			raise exception.Failure('not term lists', head, tail)


def _IterConcat(elms_iter):
		head = elms_iter.next()
		try:
			tail = _IterConcat(elms_iter)
		except StopIteration:
			return head
		else:
			return _Concat(head, tail)

def Concat(*operands):
	try:
		return _IterConcat(iter(operands))
	except StopIteration:
		return build.nil


concat = unify.Foldr(build.nil, Concat)