'''Variable.'''


class Name(str):
	'''Variable name.

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

	def __ne__(self, other):
		return self is not other


class Variable(object):
	'''Base class for context variables.

	Although this class defines the interface of some basic and common variable
	operations, the semantics of some of these operations are ocasionally specific
	to each of the derived class. Derived classes are also free to provide more
	variable operations, and the corresponding transformations.
	'''

	__slots__ = ['name']

	def __init__(self, name = None):
		if name is None:
			self.name = Name("<anonymous>")
		else:
			self.name = Name(name)

	def __repr__(self):
		name = self.__class__.__module__ + '.' + self.__class__.__name__
		return '<%s name=%s>' % (name, self.name)
