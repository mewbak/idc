"""Path to sub-terms in an aterm.
"""

import aterm
import walker


class Annotator(walker.Walker):
	"""Annotates terms with their path on the aterm tree."""

	def _setup(self):
		self.__label = self.factory.parse("Path")
		
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
		type = term.getType()
		if type in (aterm.INT, aterm.REAL, aterm.STR):
			pass
		elif type == aterm.LIST:
			term = self.annotate_list(term, path, 0)
		elif type == aterm.APPL:
			term = self.factory.makeAppl(
				term.getName(),
				self.annotate_list(term.getArgs(), path, 0),
				term.getAnnotations()
			)
		else:
			raise Failure
		return term.setAnnotation(self.__label, path)
	
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
