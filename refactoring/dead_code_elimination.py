"""Dead code elimination."""


from transf import lib
from transf import types
from transf.lib import *
import ir.match
import ir.sym


parse.Transfs(r'''

#######################################################################
# Needed/uneeded table

setUnneededVar = types.table.Del('needed')

setNeededVar = types.table.Set('needed')

setNeededVars =
    #debug.Log(`'Finding needed vars in %s\n'`, id) ;
    traverse.AllTD(
		ir.match.aSym ;
        # debug.Log(`'Found var needed %s\n'`, id) ;
		setNeededVar
	)

setAllUnneededVars = types.table.Clear('needed')

setAllNeededVars = types.table.Add('needed', 'local')

isVarNeeded =
    ir.match.aSym ;
    (?needed + Not(ir.sym.isLocalVar))


#######################################################################
# Labels

getLabelNeeded =
    Where(
        with label in
            ?GoTo(Sym(label)) <
                !label_needed ; Map(Try(?[label,<setNeededVar>])) +
                setAllNeededVars
        end
    )

setLabelNeeded =
    Where(
        with label in
            ?Label(label) ;
            !needed ;
            Map(![label,<id>] ;
            types.table.Set('label_needed'))
        end
    )


#######################################################################
# Statements

dceStmt = Proxy()
dceStmts = Proxy()

dceAssign =
    with x in
        ?Assign(_, x, _) ;
        if <ir.sym.isLocalVar> x then
            if <isVarNeeded> x then
                #debug.Log(`'******* var needed %s\n'`, !x) ;
                Where(<setUnneededVar> x );
                ~Assign(_, _, <setNeededVars>)
            else
                #debug.Log(`'******* var uneeded %s\n'`, !x) ;
                !NoStmt
            end
        else
            #debug.Log(`'******* var not local %s\n'`, !x) ;
            ~Assign(_, <setNeededVars>, <setNeededVars>)
        end
    end

dceAsm =
    ?Asm ;
    setAllNeededVars

dceLabel =
    ?Label ;
    setLabelNeeded

dceGoTo =
    ?GoTo ;
    getLabelNeeded

dceRet =
    ?Ret ;
    setAllUnneededVars ;
    ~Ret(_, <setNeededVars>)

elimBlock = {
    Block([]) -> NoStmt |
    Block([stmt]) -> stmt
}

dceBlock =
    ~Block(<dceStmts>) ;
    Try(elimBlock)

elimIf = {
    If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
    If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)
}

dceIf =
    ~If(_, <dceStmt>, _) \needed/ ~If(_, _, <dceStmt>) ;
    ~If(<setNeededVars>, _, _) ;
    Try(elimIf)

elimWhile = {
    While(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceWhile =
    \needed/* ~While(<setNeededVars>, <dceStmt>) ;
    Try(elimWhile)

elimDoWhile = {
    DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)
}

dceDoWhile =
    ~DoWhile(<setNeededVars>, _) ;
    \needed/* ~DoWhile(_, <dceStmt>) ;
    Try(elimDoWhile)

dceFunction =
    ir.sym.EnterFunction(
    with label_needed[] in
        ~Function(_, _, _, <
            \label_needed/* with needed[] in dceStmts end
        >)
    end
    )

# If none of the above applies, assume all vars are needed
dceDefault =
    setAllNeededVars

dceStmt.subject =
    ?Assign < dceAssign +
    ?Asm < dceAsm +
    ?Label < dceLabel +
    ?GoTo < dceGoTo +
    ?Ret < dceRet +
    ?Block < dceBlock +
    ?If < dceIf +
    ?While < dceWhile +
    ?DoWhile < dceDoWhile +
    ?Function < dceFunction +
    ?Var < id +
    ?NoStmt

dceStmts.subject =
    MapR(dceStmt) ;
    Filter(Not(?NoStmt))

dceModule =
    ~Module(<dceStmts>)

dce =
    with needed[], local[], label_needed[] in
        dceModule
    end


#######################################################################
# Refactoring

applicable = id
input = ![]
apply = dce


#######################################################################
# Tests

testNoStmt =
    !Module([NoStmt]) ;
    dce ;
    ?Module([])

testAssign =
    !Module([
        Function(Int(32,Signed),"f",[],[
            Assign(Int(32,Signed),Sym("ebx"){Reg},Lit(Int(32,Signed),1)),
            Ret(Int(32,Signed),Sym("eax"){Reg})
        ])
    ]) ;
    dce ;
    ?Module([
         Function(Int(32,Signed),"f",[],[
            Ret(Int(32,Signed),Sym("eax"){Reg})
        ])
    ])

''')
