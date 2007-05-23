'''Path/selection related transformations.'''


from transf import parse
import ir.match


parse.Transfs(r'''

#######################################################################
# Path annotation

# Only annotate term applications
annotate = path.Annotate(
	match.ApplNames(`
		ir.match.stmtNames +
		ir.match.exprNames +
		ir.match.typeNames
	`)
)


#######################################################################
# Selection

projectSelection = path.Project(!selection)

MatchSelectionTo(s) = projectSelection ; s


#######################################################################
# Selection context

getSelection = !selection

isSelected =
	Where(
		path.get ;
		path.Equals(getSelection)
	)

inSelection =
	Where(
		path.get ;
		path.Contained(getSelection)
	)

hasSelection =
	Where(
		path.get ;
		path.Contains(getSelection)
	)

''')
