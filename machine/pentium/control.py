'''Control transfer instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''

asmJMP =
	[Ref(addr)] -> [GoTo(addr)]

AsmJcc(cond) =
	[Ref(addr)] -> [If(<cond>,GoTo(addr),NoStmt)]

asmJA = AsmJcc(LAnd(LNot(cf),LNot(zf)))
asmJE = AsmJcc(zf)
asmJLE = AsmJcc(LAnd(LNot(zf),LNotEq(sf,of)))
asmJBE = AsmJcc(LOr(cf,zf))
asmJNE = AsmJcc(LNot(zf))
asmJG = AsmJcc(LAnd(LNot(zf),LEq(sf,of)))
#TODO: complete remaining

asmCALL =
	[Ref(addr)] -> [Assign(Void, NoExpr, Call(addr,[]))]

asmRET =
	[] -> [Ret(Void, NoExpr)]

''')


