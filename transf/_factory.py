'''Helper transformation factory for short-cutting code.'''


from transf import match
from transf import traverse


class ApplFactory(object):

	def __init__(self, name):
		self.name = match.MatchStr(name)
	
	def __call__(self, *args):
		return traverse.TraverseAppl(self.name, traverse.TraverseList(args))
		

class Factory(object):

	def __getattribute__(self, name):
		if name and name[0].isupper() and name.isalpha():
			return ApplFactory(name)
		else:
			raise AttributeError