'''Helper transformation factory for short-cutting code.'''


from transf import matching
from transf import traversal


class ApplFactory(object):

	def __init__(self, name):
		self.name = matching.MatchStr(name)
	
	def __call__(self, *args):
		return traversal.TraverseAppl(self.name, traversal.TraverseList(args))
		

class Factory(object):

	def __getattribute__(self, name):
		if name and name[0].isupper() and name.isalpha():
			return ApplFactory(name)
		else:
			raise AttributeError