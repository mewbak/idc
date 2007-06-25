'''Control transfer instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.conditions import *


parse.Transfs('''

asmJMP =
	[Ref(addr)] -> [GoTo(addr)]


AsmJcc(cond) =
	[Ref(addr)] -> [If(<cond>,GoTo(addr),NoStmt)]

asmJA    = AsmJcc(ccA   )
asmJAE   = AsmJcc(ccAE  )
asmJB    = AsmJcc(ccB   )
asmJBE   = AsmJcc(ccBE  )
asmJC    = AsmJcc(ccC   )
asmJCXZ  = AsmJcc(ccCXZ )
asmJECXZ = AsmJcc(ccECXZ)
asmJE    = AsmJcc(ccE   )
asmJG    = AsmJcc(ccG   )
asmJGE   = AsmJcc(ccGE  )
asmJL    = AsmJcc(ccL   )
asmJLE   = AsmJcc(ccLE  )
asmJNA   = AsmJcc(ccNA  )
asmJNAE  = AsmJcc(ccNAE )
asmJNB   = AsmJcc(ccNB  )
asmJNBE  = AsmJcc(ccNBE )
asmJNC   = AsmJcc(ccNC  )
asmJNE   = AsmJcc(ccNE  )
asmJNG   = AsmJcc(ccNG  )
asmJNGE  = AsmJcc(ccNGE )
asmJNL   = AsmJcc(ccNL  )
asmJNLE  = AsmJcc(ccNLE )
asmJNO   = AsmJcc(ccNO  )
asmJNP   = AsmJcc(ccNP  )
asmJNS   = AsmJcc(ccNS  )
asmJNZ   = AsmJcc(ccNZ  )
asmJO    = AsmJcc(ccO   )
asmJP    = AsmJcc(ccP   )
asmJPE   = AsmJcc(ccPE  )
asmJPO   = AsmJcc(ccPO  )
asmJS    = AsmJcc(ccS   )
asmJZ    = AsmJcc(ccZ   )


asmCALL =
	[Ref(addr)] -> [Assign(Void, NoExpr, Call(addr,[]))]


asmRET =
	[] -> [Ret(Void, NoExpr)]


''')



