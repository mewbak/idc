'''Term pattern makeing.'''


from aterm.factory import factory


class Build(object):
	'''Build object.'''
	
	def __init__(self, args, kargs):
		self.args = args
		self.kargs = kargs


class Builder(object):

	def build(self, *args, **kargs):
		build = Build(list(args), kargs)
		return self._build(build)
		
	def _build(self, build):
		raise NotImplementedError
	

class Term(Builder):
	
	def __init__(self, term):
		Builder.__init__(self)
		self.term = term
	
	def _build(self, build):
		return self.term


def Int(value):
	return Term(factory.makeInt(value))


def Real(value):
	return Term(factory.makeReal(value))


def Str(value):
	return Term(factory.makeStr(value))

	
def Nil():
	return Term(factory.makeNil())


class Cons(Builder):
	
	def __init__(self, head, tail):
		Builder.__init__(self)
		assert isinstance(head, Builder)
		assert isinstance(tail, Builder)
		self.head = head
		self.tail = tail
	
	def _build(self, build):
		return factory.makeCons(
			self.head._build(build),	
			self.tail._build(build)
		)


class Appl(Builder):
	
	def __init__(self, name, args):
		Builder.__init__(self)
		assert isinstance(name, Builder)
		assert isinstance(args, Builder)
		self.name = name
		self.args = args
	
	def _build(self, build):
		return factory.makeAppl(
			self.name._build(build),	
			self.args._build(build)
		)


class Wildcard(Builder):
	
	def _build(self, build):
		return build.args.pop(0)


class Var(Builder):
	
	def __init__(self, name):
		Builder.__init__(self)
		assert isinstance(name, basestring)
		self.name = name
	
	def _build(self, build):
		return build.kargs[self.name]
