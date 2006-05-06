'''Path to sub-terms in an aterm.
'''


class Annotator:
	"""Annotates terms with their path on the aterm tree."""

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
		| f(*a) # f(*:anno_args(path, 0))
			{ $a = self.anno_args($a, $path, self.factory.makeInt(0)) }
			->	f(*a)
		| _
		;

	anno_list(path, index)
		"""Annotate a list of terms."""
		: []
		| [head, *tail] -> 
			[
				:anno_term(head, [Index(index), *path]), 
				*:anno_list(tail, path, { self.factory.makeInt($index.getValue() + 1) })
			]
		;
	
	anno_args(path, index)
		"""Annotate a application term's argument list."""
		: []
		| [head, *tail] -> 
			[
				:anno_term(head, [Arg(index), *path]), 
				*:anno_args(tail, path, { self.factory.makeInt($index.getValue() + 1) })
			]
		;

