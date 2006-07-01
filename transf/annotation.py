'''High-level annotation transformations.'''


from transf import exception
from transf import base
from transf import scope
from transf import combine
from transf import match
from transf import build
from transf import congruent
from transf import project
from transf import lists
from transf import debug


def Set(label, *values):
	annos = scope.Anonymous('annos')
	return scope.Let2((
			(annos, build.List(values)),
		),
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
