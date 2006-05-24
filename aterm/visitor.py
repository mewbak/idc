'''Term visiting.'''


class Visitor:
	'''Base class for term visitors.'''
	
	def __init__(self):
		pass
	
	def __call__(self, term, *args, **kargs):
		return self.visit(term, *args, **kargs)
		
	def visit(self, term, *args, **kargs):
		'''Visit the given term.'''
		return term.accept(self, *args, **kargs)

	def visitTerm(self, term, *args, **kargs):
		raise NotImplementedError

	def visitLit(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
		
	def visitInt(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitReal(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitStr(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)
	
	def visitList(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitNil(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitCons(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitAppl(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitPlaceholder(self,term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
		
	def visitWildcard(self, term, *args, **kargs):
		return self.visitPlaceholder(term, *args, **kargs)

	def visitVar(self, term, *args, **kargs):
		return self.visitPlaceholder(term, *args, **kargs)



class IncrementalVisitor(Visitor):
	'''Visitor which incrementally builds up a modified term.'''
	
	def visitHead(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitTail(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitCons(self, term, *args, **kargs):
		old_head = term.getHead()
		old_tail = term.getTail()
		new_head = self.visitHead(old_head, *args, **kargs)
		new_tail = self.visitTail(old_tail, *args, **kargs)
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(new_head, new_tail, term.getAnnotations())
		else:
			return term

	def visitName(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
	
	def visitArgs(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)
	
	def visitAppl(self, term, *args, **kargs):
		old_name = term.getName()
		old_args = term.getArgs()
		new_name = self.visitName(old_name, *args, **kargs)
		new_args = self.visitArgs(old_args, *args, **kargs)
		if new_name is not old_name or new_args is not old_args:
			return term.factory.makeAppl(new_name, new_args, term.getAnnotations())
		else:
			return term
