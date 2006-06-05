'''Builtin lookup table.'''


from transf import combine
from transf import traverse
from transf import unify


builtins = {
	"id": combine.Ident(),
	"fail": combine.Fail(),
	"all": traverse.All,
	#"one": traverse.One,
	#"some": traverse.Some,
	"not": combine.Not,
	"where": combine.Where,
	"map": traverse.Map,
	"foldr": unify.Foldr,
}
