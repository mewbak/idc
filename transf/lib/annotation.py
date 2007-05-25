'''High-level annotation transformations.'''


from transf import exception
from transf import types
from transf.lib import base
from transf.lib import scope
from transf.lib import combine
from transf.lib import match
from transf.lib import build
from transf.lib import congruent
from transf.lib import project
from transf.lib import lists
from transf.lib import debug


def Set(label, *values):
	annos = types.term.Term('annos')
	return scope.Scope((annos,),
		combine.Where(build.List(values) * annos.match) *
		congruent.Annos(
			lists.Fetch(congruent.ApplCons(match.Str(label), build.Var(annos))) +
			build.Cons(build.ApplCons(build.Str(label), build.Var(annos)), base.ident)
		),
	)


def Update(label, *values):
	return congruent.Annos(
		lists.Fetch(congruent.Appl(label, values))
	)


def Get(label):
	return (
		project.annos *
		project.Fetch(match.ApplName(label)) *
		project.args *
		combine.If(
			match.Cons(base.ident, match.nil),
			project.head
		)
	)


def Del(label):
	return congruent.Annos(
		+(
			lists.Filter(
				-match.ApplName(label)
			)
		)
	)
