'''Context term variables.'''


from transf import exception
from transf import base
from transf.types import variable


class Term(variable.Variable):
	'''Term variable.'''

	__slots__ = ['term']

	def __init__(self, term = None):
		variable.Variable.__init__(self)
		self.term = term

	def set(self, term):
		self.term = term

	def unset(self):
		self.term = None

	def match(self, term):
		'''Match the term against this variable value, setting it,
		if it is undefined.'''
		if self.term is None:
			self.term = term
		elif self.term != term:
			raise exception.Failure('variable mismatch', term, self.term)

	def build(self):
		'''Returns this variable term, if defined.'''
		if self.term is None:
			raise exception.Failure('undefined variable')
		else:
			return self.term

	def traverse(self, term):
		'''Same as match.'''
		self.match(term)
		return term

	def __repr__(self):
		return '<%s.%s %r>' % (__name__, self.__class__.__name__, self.term)


class New(variable.Constructor):
	'''Creates a new term variable without an initial value.'''
	def create(self, term, ctx):
		return Term()

new = New()


class Transf(variable.Constructor):
	'''Creates a new term variable with a initial value
	given by a transformation.'''
	def __init__(self, transf):
		variable.Constructor.__init__(self)
		self.transf = transf
	def create(self, term, ctx):
		term = self.transf.apply(term, ctx)
		return Term(term)

