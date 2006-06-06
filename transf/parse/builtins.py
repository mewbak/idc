'''Builtin lookup table.'''


from transf import base
from transf import combine
from transf import traverse
from transf import unify
from transf import lists


builtins = {
	"id": base.ident,
	"fail": base.fail,
	"all": traverse.All,
	#"one": traverse.One,
	#"some": traverse.Some,
	"not": combine.Not,
	"where": combine.Where,
	"map": traverse.Map,
	"foldr": unify.Foldr,
	"concat": lists.Concat,
}
