'''Support for transformation context.'''


class Anonymous(str):
	'''Anonymous variable -- a string with an unique hash.'''
	
	__slots__ = []
	
	def __hash__(self):
		return id(self)
	
	def __eq__(self, other):
		return self is other


class Context(dict):
	'''Transformation context -- a nested dictionary.'''
	
	__slots__ = ['parent']
	
	def __init__(self, names = None, parent = None):
		dict.__init__(self)
		if names:
			for name in names:
				dict.__setitem__(self, name, None)
		self.parent = parent
	
	def __contains__(self, name):
		if dict.__contains__(self, name):
			return True
		elif self.parent is not None:
			return name in self.parent
		else:
			return False
	
	def __getitem__(self, name):
		if dict.__contains__(self, name):
			return dict.__getitem__(self, name)
		elif self.parent is not None:
			return self.parent[name]
		else:
			raise KeyError
	
	def __len__(self):
		return len(self.keys())

	def __setitem__(self, name, value):
		if dict.__contains__(self, name):
			dict.__setitem__(self, name, value)
		elif self.parent is not None:
			self.parent[name] = value
		else:
			raise KeyError
	
	def __repr__(self):
		return repr(dict(self.iteritems()))

	def items(self):
		return list(self.iteritems())

	def keys(self):
		return list(self.iterkeys())

	def values(self):
		return list(self.itervalues())

	def iteritems(self):
		for name, value in dict.iteritems(self):
			yield name, value
		if self.parent is not None:
			for name, value in self.parent.iteritems():
				if not dict.__contains__(self, name):
					yield name, value

	def iterkeys(self):
		for name, value in self.iteritems():
			yield name

	__iter__ = iterkeys
	
	def itervalues(self):
		for name, value in self.iteritems():
			yield value
	
	def update(self, other):
		for name, value in other.iteritems():
			self[name] = value

