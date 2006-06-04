'''Builtin lookup table.'''


from transf import combinators
from transf import traversal
from transf import unifiers


builtins = {
	"id": combinators.Ident(),
	"fail": combinators.Fail(),
	"all": traversal.All,
	#"one": traversal.One,
	#"some": traversal.Some,
	"not": combinators.Not,
	"where": combinators.Where,
	"map": traversal.Map,
	"foldr": unifiers.Foldr,
}
