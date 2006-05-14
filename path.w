'''Path to sub-terms in an aterm.
'''


class Annotator:
	"""Annotates terms with their path on the aterm tree."""

{
	def annotate(cls, term):
		annotator = cls(term.factory)
		return annotator.anno(term)
	annotate = classmethod(annotate)
}

	anno
		"""Annotate the root term."""
		: x -> :anno_term(x, [])
		;
	
	anno_term(path)
		"""Annotate a term with paths relative to the given path."""
		: x -> :anno_subterms(x, path)
			{ $$ = $$.setAnnotation(self.factory.parse("Path"), path) }
		;
		
	anno_subterms(path)
		"""Recursively annotates the sub-terms with paths relative to the given path."""
		: l:_list -> :anno_list(l, path, 0)
		| f(*a) # f(*:anno_list(path, 0))
			{ $a = self.anno_list($a, $path, self.factory.makeInt(0)) }
			->	f(*a)
		| _
		;

	anno_list(path, index)
		"""Annotate a list of terms."""
		: []
		| [head, *tail] -> 
			[
				:anno_term(head, [index, *path]), 
				*:anno_list(tail, path, { self.factory.makeInt($index.getValue() + 1) })
			]
		;

