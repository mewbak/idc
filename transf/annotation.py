'''High-level annotation transformations.'''


from transf import exception
from transf import base
from transf import scope
from transf import combine
from transf import match
from transf import build
from transf import traverse
from transf import project
from transf import debug


def Set(label, *values):
	annos_var = build.Var('annos')
	return scope.Let(
		traverse.Annos(
			traverse.One(traverse.Appl(match.Str(label), annos_var))
			| build.Cons(build.Appl(build.Str(label), annos_var), base.ident)
		),
		annos = build.List(values)
	)


def Update(label, *values):
	values = traverse.List(values)
	return traverse.Annos(
		traverse.One(traverse.Appl(match.Str(label), values))
	)


def Get(label):
	return project.annos \
		& project.Fetch(match.Appl(match.Str(label), base.ident)) \
		& project.args \
		& combine.IfThen(
			match.Cons(base.ident, match.nil), 
			project.head
		)


def Del(label):
	return traverse.Annos(
		combine.Try(
			traverse.Filter(
				combine.Not(match.Appl(match.Str(label), base.ident))
			)
		)
	)
