'''Support for transformation context.'''


import UserDict

try:
	set
except NameError:
	from sets import ImmutableSet as set


class Context(UserDict.DictMixin):
	
	def __init__(self, parent = None, locals = ()):
		self.parent = parent
		self.locals = set(locals)
		self.values = {}
	
	def __getitem__(self, name):
		try:
			return self.values[name]
		except KeyError:
			if self.parent is not None and name not in self.locals:
				return self.parent[name]
			else:
				raise
	
	def _updateitem(self, name, value):
		if name in self.values or name in self.locals:
			self.values[name] = value
		elif parent is not None:
			self.parent._updateitem(name, value)
		else:
			raise KeyError
			
	def __setitem__(self, name, value):
		try:
			self._updateitem(name, value)
		except KeyError:
			self.values[name] = value
	
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
		