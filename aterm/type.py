'''Type verification.'''


from aterm import visitor


class _Typer(visitor.Visitor):
	'''Base class for all type verificators.'''
	
	def visitTerm(self, term):
		return False


class _Int(_Typer):
	'''Integer term type verifier.'''
	
	def visitInt(self, term):
		return True

anInt = _Int().visit


class _Real(_Typer):
	'''Real term type verifier.'''
	
	def visitReal(self, term):
		return True

aReal = _Real().visit


class _Str(_Typer):
	'''String term type verifier.'''

	def visitStr(self, term):
		return True

aStr = _Str().visit


class _Lit(_Typer):
	'''Literal term type verifier.'''
	
	def visitLit(self, term):
		return True

aLit = _Lit().visit


class _Nil(_Typer):
	'''Empty list term type verifier.'''
	
	def visitNil(self, term):
		return True

aNil = _Nil().visit


class _Cons(_Typer):
	'''List construction term type verifier.'''
	
	def visitCons(self, term):
		return True

aCons = _Cons().visit


class _List(_Typer):
	'''List term type verifier.'''
	
	def visitList(self, term):
		return True

aList = _List().visit


class _Appl(_Typer):
	'''Application term type verifier.'''
	
	def visitAppl(self, term):
		return True

anAppl = _Appl().visit
