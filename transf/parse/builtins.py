'''Builtin lookup table.'''


from transf import base
from transf import combine
from transf import traverse
from transf import unify
from transf import lists
from transf import strings
from transf import arith


builtins = {
	"id": base.ident,
	"fail": base.fail,
	
	"try": combine.Try,
	"not": combine.Not,
	"where": combine.Where,

	"map": traverse.Map,
	"filter": traverse.Filter,
	"filterr": traverse.FilterR,
	"all": traverse.All,
	"one": traverse.One,
	"some": traverse.Some,
	"alltd": traverse.AllTD,
	
	"foldr": unify.Foldr,

	"concat": lists.Concat,
	
	"str": strings.ToStr,
	
	"neg": arith.Neg,
	"add": arith.Add,
	"sub": arith.Sub,
	"gt": arith.Gt,

}
