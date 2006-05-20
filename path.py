"""Path to sub-terms in an aterm.
"""

import aterm
import walker


class Annotator(walker.Walker):
	"""Annotates terms with their path on the aterm tree."""

	def annotate(cls, term):
		"""Class method which returns an equivalent term with annotated paths."""
		annotator = cls(term.factory)
		return annotator.annotate_root(term)
	annotate = classmethod(annotate)

	def annotate_root(self, term):
		"""Annotate the root term."""
		return self.annotate_term(term, self.factory.makeNilList())
	
	def annotate_term(self, term, path):
		"""Recursively annotates a term with paths relative to the given path."""
		type_ = term.getType()
		if type_ in (aterm.INT, aterm.REAL, aterm.STR):
			pass
		elif type_ == aterm.LIST:
			term = self.annotate_list(term, path, 0)
		elif type_ == aterm.APPL:
			term = self.factory.makeAppl(
				term.getName(),
				self.annotate_list(term.getArgs(), path, 0),
				term.getAnnotations()
			)
		else:
			raise walker.Failure
		return term.setAnnotation(self.factory.parse("Path"), path)
	
	def annotate_list(self, term, path, index):
		"""Annotate a list of terms."""
		self._list(term)
		if term.isEmpty():
			return term
		else:
			return self.factory.makeConsList(
				self.annotate_term(
					term.getHead(), 
					self.factory.makeConsList(
						self.factory.makeInt(index), 
						path
					)
				),
				self.annotate_list(term.getTail(), path, index + 1),
				term.getAnnotations()
			)


class Evaluator(walker.Walker):
	"""Evaluates a path on a term."""
	
	def evaluate(cls, term, path):
		"""Class method which evaluates the given term."""
		return cls(term.factory).evaluate_term(term, path)
	evaluate = classmethod(evaluate)

	def evaluate_term(self, term, path):
		"""Recursively evaluates a term with paths relative to the given path."""
		
		if path.isEmpty():
			return term
		
		tail = path.getTail()		
		term = self.evaluate_term(term, tail)
		
		head = path.getHead()
		index = head.getValue()
		
		type_ = term.getType()
		if type_ == aterm.LIST:
			return term[index]
		elif type_ == aterm.APPL:
			return term.getArgs()[index]
		else:
			raise walker.Failure
		return term.setAnnotation(self.factory.parse("Path"), path)

