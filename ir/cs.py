'''Control structures recognition.'''


from transf import *
import ir.match


#######################################################################
# Statements

parse.Transfs(r'''

liftIfThen =
		with cond, label, rest in
			~[If(cond, GoTo(Sym(label)), NoStmt), *<AtSuffix(
				?[Label(label), *] ; ?rest ; 
				![]
			)>] ;
			![If(Unary(Not(Bool), cond), Block(<project.tail>), NoStmt), *rest]
		end

# TODO: liftIfThenElse

liftLoop =
		with label, rest in
			~[Label(label), *<AtSuffix(
				?[GoTo(Sym(label)), *rest] ; 
				![]
			) ; 
			![While(Lit(Bool,1), Block(<id>)), *rest]
			>]
		end

liftWhile =
		with label, cond, rest in
			~[Label(label), *<AtSuffix(
				?[If(_,GoTo(Sym(label)),NoStmt), *] ; 
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

