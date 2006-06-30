'''Path/selection related transformations.'''


import transf as lib
import ir.match


#######################################################################
# Path annotation

# Only annotate term applications
annotate = lib.path.Annotate(
	ir.match.ApplNames(
		ir.match.stmtNames +
		ir.match.exprNames +
		ir.match.typeNames
	)
)


#######################################################################
# Selection

lib.parse.Transfs(r'''

projectSelection = lib.path.Project(!selection)

MatchSelectionTo(s) = projectSelection ; s 

''')


#######################################################################
# Selection context

lib.parse.Transfs(r'''

getSelection = !selection

isSelected = 
	Where( 
		lib.path.get ; 
		lib.path.Equals(getSelection) 
	)

inSelection = 
	Where(
		lib.path.get ;
		lib.path.Contained(getSelection)
	)

hasSelection =
	Where(
		lib.path.get ;
		lib.path.Contains(getSelection)
	)

''')
