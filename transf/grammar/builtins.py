'''Builtin lookup table.'''


from transf import combinators
from transf import traversal


builtins = {
	"all": traversal.All,
	#"one": traversal.One,
	#"some": traversal.Some,
	"not": combinators.Not,
	"where": combinators.Where,
}
