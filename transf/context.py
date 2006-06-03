'''Support for transformation context.'''


import UserDict


class Context(UserDict.DictMixin):
	
	def __init__(self, parent = None, locals = ()):
		self.parent = parent
		self.locals = locals
		self.values = {}
	
	def __getitem__(self, name):
		try:
			return self.values[name]
		except KeyError:
			if self.parent is not None and name not in self.locals:
				return self.parent[name]
			else:
				raise
	
	def __setitem__(self, name, value):
		try:
			self.values[name]
		except KeyError:
			self.values[name] = value
		else:
			raise KeyError
	
	def keys(self):
		keys = self.values.keys()
		if self.parent is not None:
			for key in self.parent:
				if key not in self.locals:
					keys.append(key)
		return keys

	def iteritems(self):
		for name, value in self.values.iteritems():
			yield name, value
		if self.parent is not None:
			for name, value in self.parent.iteritems():
				if name not in self.locals:
					yield name, value
		raise StopIteration
		