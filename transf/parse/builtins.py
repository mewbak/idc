'''Builtin lookup table.'''


from transf import base
from transf import combine
from transf import traverse
from transf import unify


builtins = {
	"id": base.Ident(),
	"fail": base.Fail(),
	"all": traverse.All,
	#"one": traverse.One,
	#"some": traverse.Some,
	"not": combine.Not,
	"where": combine.Where,
	"map": traverse.Map,
	"foldr": unify.Foldr,
}
