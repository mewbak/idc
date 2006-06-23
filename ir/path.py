'''Path annotation.'''


import transf as lib
import ir.match


# Only annotate term applications
annotate = lib.path.Annotate(
	ir.match.ApplNames(
		ir.match.stmtNames +
		ir.match.exprNames +
		ir.match.typeNames
	)
)
