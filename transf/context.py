'''Transformation contexts.'''

__docformat__ = 'epytext'


from transf import exception


class Anonymous(str):
	'''Anonymous variable name. 
	
	This class is a string with singleton properties, i.e., it has an unique hash,
	and it is equal to no object other than itself. Instances of this class can be
	used in replacement of regular string to ensure no name collisions will ocurr,
	effectivly providing means to anonymous variables.
	'''
	
	__slots__ = []
	
	def __hash__(self):
		return id(self)
	
	def __eq__(self, other):
		return self is other


class Context(object):
	'''Transformation context.
	
	Contexts are nested dictionaries of named variables. During variable lookup,
	variables not found in the local scope are search recursively in the ancestor
	contexts.
	'''
	
	__slots__ = ['vars', 'parent']
	
	def __init__(self, vars = (), parent = None):
		'''Create a new context.
		
		@param vars: a sequence/iterator of (name, variable) pairs.
		@param parent: optional parent context.
		'''
		self.vars = dict(vars)
		self.parent = parent
	
	def get(self, name):
		'''Lookup the variable with this name.'''
		try:
			return self.vars[name]
		except KeyError:
			if self.parent is not None:
				return self.parent.get(name)
			else:
				raise exception.Fatal('undeclared variable', name)
	
	__getitem__ = get
	
	def iter(self):
		'''Iterate over all variables defined in this context.
		'''
		if self.parent is not None:
			for name, var in self.parent:
				if name not in self.vars:
					yield name, var
		for name, var in self.vars.iteritems():
			yield name, var
		raise StopIteration
	
	__iter__ = iter
	
	def __repr__(self):
		return repr(self.vars)

empty = Context()
