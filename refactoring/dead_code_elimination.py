"""Dead code elimination."""


from transf import lib
import ir.dce

applicable = lib.base.ident

input = lib.build.empty

apply = ir.dce.dce
