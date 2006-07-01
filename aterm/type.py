'''Type matching.'''


from aterm import visitor


class Typer(visitor.Visitor):
	
	def visitTerm(self, term):
		return False


class Int(Typer):
	
	def visitInt(self, term):
		return True

anInt = Int().visit

class Real(Typer):
	
	def visitReal(self, term):
		return True

aReal = Real().visit

class Str(Typer):
	
	def visitStr(self, term):
		return True

aStr = Str().visit

class Lit(Typer):
	
	def visitLit(self, term):
		return True

aLit = Lit().visit


class Nil(Typer):
	
	def visitNil(self, term):
		return True

aNil = Nil().visit


class List(Typer):
	
	def visitList(self, term):
		return True

aList = List().visit

class Appl(Typer):
	
	def visitAppl(self, term):
		return True

anAppl = Appl().visit
