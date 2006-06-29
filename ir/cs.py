'''Control structures recognition.'''


from transf import *
import ir.match
import ir.path

#######################################################################
# Statements

parse.Transfs(r'''

goto =  
	ir.path.isSelected ;
	?GoTo(Sym(label))

liftIfThen =
		with cond, label, rest in
			~[If(cond, <goto>, NoStmt), *<AtSuffix(
				?[Label(label), *] ; ?rest ; 
				![]
			)>] ;
			![If(Unary(Not(Bool), cond), Block(<project.tail>), NoStmt), *rest]
		end

# TODO: liftIfThenElse

liftLoop =
		with label, rest in
			~[Label(label), *<AtSuffix(
				?[<goto>, *rest] ; 
				![]
			) ; 
			![While(Lit(Bool,1), Block(<id>)), *rest]
			>]
		end

liftWhile =
		with label, cond, rest in
			~[Label(label), *<AtSuffix(
				?[If(_,<goto>,NoStmt), *] ; 
				?[If(cond,_,_), *rest] ; 
				![]
			) ; 
			# XXX: this should be a DoWhile, and not a While
			![While(cond, Block(<id>)), *rest]
			>]
		end


lift = AtSuffixR(liftIfThen + liftLoop + liftWhile)

do = BottomUp(Repeat(lift))
''')

