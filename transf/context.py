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
	
	__slots__ = ['_p']
	
	def __init__(self, keys = None, parent = None):
		dict.__init__(self)
		if keys:
			for k in keys:
				dict.__setitem__(self, k, None)
		self._p = parent
	
	def __contains__(self, k):
		if dict.__contains__(self, k):
			return True
		elif self._p is not None:
			return k in self._p
		else:
			return False
	
	def __getitem__(self, k):
		if dict.__contains__(self, k):
			return dict.__getitem__(self, k)
		elif self._p is not None:
			return self._p[k]
		else:
			raise KeyError
	
	def __len__(self):
		return len(self.keys())

	def __setitem__(self, k, v):
		if dict.__contains__(self, k):
			dict.__setitem__(self, k, v)
		elif self._p is not None:
			self._p[k] = v
		else:
			raise KeyError(k)
	
	def __delitem__(self, k):
		if dict.__contains__(self, k):
			dict.__setitem__(self, k, None)
		elif self._p is not None:
			del self._p[k]
		else:
			raise KeyError(k)
	
	def setdefault(self, k, v):
		try:
			r = dict.__getitem__(self, k)
		except KeyError:
			if self._p is not None:
				return self._p.setdefault(k, v)
			else:
				raise KeyError(k)
		else:
			if r is None:
				dict.__setitem__(self, k, v)
				return v
			else:
				return r
		
	def items(self):
		return list(self.iteritems())

	def keys(self):
		return list(self.iterkeys())

	def values(self):
		return list(self.itervalues())

	def iteritems(self):
		for k, v in dict.iteritems(self):
			yield k, v
		if self._p is not None:
			for k, v in self._p.iteritems():
				if not dict.__contains__(self, k):
					yield k, v

	def iterkeys(self):
		for k, v in self.iteritems():
			yield k

	__iter__ = iterkeys
	
	def itervalues(self):
		for k, v in self.iteritems():
			yield v
	
	def update(self, o):
		for k, v in o.iteritems():
			self[k] = v

	def __repr__(self):
		return repr(dict(self.iteritems()))

