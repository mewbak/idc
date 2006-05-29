'''Helper transformation factory for short-cutting code.'''


from transf.term import Str, List, Appl


class ApplFactory(object):

	def __init__(self, name):
		self.name = Str(name)
	
	def __call__(self, *args):
		return Appl(self.name, List(args))
		

class Factory(object):

	def __getattribute__(self, name):
		if name and name[0].isupper() and name.isalpha():
			return ApplFactory(name)
		else:
			raise AttributeError