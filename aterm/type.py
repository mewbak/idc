'''Type verification.'''


from aterm import visitor


class Typer(visitor.Visitor):
	'''Base class for all type verificators.'''
	
	def visitTerm(self, term):
		return False


class Int(Typer):
	'''Integer term type verifier.'''
	
	def visitInt(self, term):
		return True

anInt = Int().visit


class Real(Typer):
	'''Real term type verifier.'''
	
	def visitReal(self, term):
		return True

aReal = Real().visit


class Str(Typer):
	'''String term type verifier.'''

	def visitStr(self, term):
		return True

aStr = Str().visit


class Lit(Typer):
	'''Literal term type verifier.'''
	
	def visitLit(self, term):
		return True

aLit = Lit().visit


class Nil(Typer):
	'''Empty list term type verifier.'''
	
	def visitNil(self, term):
		return True

aNil = Nil().visit


class Cons(Typer):
	'''List construction term type verifier.'''
	
	def visitCons(self, term):
		return True

aCons = Cons().visit


class List(Typer):
	'''List term type verifier.'''
	
	def visitList(self, term):
		return True

aList = List().visit


class Appl(Typer):
	'''Application term type verifier.'''
	
	def visitAppl(self, term):
		return True

anAppl = Appl().visit
