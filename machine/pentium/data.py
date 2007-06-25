'''Data transfer instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.conditions import *

parse.Transfs('''

AsmMOV(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,src)]

asmMOVB = AsmMOV(!8)
asmMOVW = AsmMOV(!16)
asmMOVL = AsmMOV(!32)


AsmCMOVcc(size,cond) =
	[dst,src] -> [If(<cond>,Assign(<Word(size)>,dst,src),NoStmt)]

asmCMOVAW   = AsmCMOVcc(!16, ccA   )
asmCMOVAEW  = AsmCMOVcc(!16, ccAE  )
asmCMOVBW   = AsmCMOVcc(!16, ccB   )
asmCMOVBEW  = AsmCMOVcc(!16, ccBE  )
asmCMOVCW   = AsmCMOVcc(!16, ccC   )
asmCMOVEW   = AsmCMOVcc(!16, ccE   )
asmCMOVGW   = AsmCMOVcc(!16, ccG   )
asmCMOVGEW  = AsmCMOVcc(!16, ccGE  )
asmCMOVLW   = AsmCMOVcc(!16, ccL   )
asmCMOVLEW  = AsmCMOVcc(!16, ccLE  )
asmCMOVNAW  = AsmCMOVcc(!16, ccNA  )
asmCMOVNAEW = AsmCMOVcc(!16, ccNAE )
asmCMOVNBW  = AsmCMOVcc(!16, ccNB  )
asmCMOVNBEW = AsmCMOVcc(!16, ccNBE )
asmCMOVNCW  = AsmCMOVcc(!16, ccNC  )
asmCMOVNEW  = AsmCMOVcc(!16, ccNE  )
asmCMOVNGW  = AsmCMOVcc(!16, ccNG  )
asmCMOVNGEW = AsmCMOVcc(!16, ccNGE )
asmCMOVNLW  = AsmCMOVcc(!16, ccNL  )
asmCMOVNLEW = AsmCMOVcc(!16, ccNLE )
asmCMOVNOW  = AsmCMOVcc(!16, ccNO  )
asmCMOVNPW  = AsmCMOVcc(!16, ccNP  )
asmCMOVNSW  = AsmCMOVcc(!16, ccNS  )
asmCMOVNZW  = AsmCMOVcc(!16, ccNZ  )
asmCMOVOW   = AsmCMOVcc(!16, ccO   )
asmCMOVPW   = AsmCMOVcc(!16, ccP   )
asmCMOVPEW  = AsmCMOVcc(!16, ccPE  )
asmCMOVPOW  = AsmCMOVcc(!16, ccPO  )
asmCMOVSW   = AsmCMOVcc(!16, ccS   )
asmCMOVZW   = AsmCMOVcc(!16, ccZ   )

asmCMOVAL   = AsmCMOVcc(!32, ccA   )
asmCMOVAEL  = AsmCMOVcc(!32, ccAE  )
asmCMOVBL   = AsmCMOVcc(!32, ccB   )
asmCMOVBEL  = AsmCMOVcc(!32, ccBE  )
asmCMOVCL   = AsmCMOVcc(!32, ccC   )
asmCMOVEL   = AsmCMOVcc(!32, ccE   )
asmCMOVGL   = AsmCMOVcc(!32, ccG   )
asmCMOVGEL  = AsmCMOVcc(!32, ccGE  )
asmCMOVLL   = AsmCMOVcc(!32, ccL   )
asmCMOVLEL  = AsmCMOVcc(!32, ccLE  )
asmCMOVNAL  = AsmCMOVcc(!32, ccNA  )
asmCMOVNAEL = AsmCMOVcc(!32, ccNAE )
asmCMOVNBL  = AsmCMOVcc(!32, ccNB  )
asmCMOVNBEL = AsmCMOVcc(!32, ccNBE )
asmCMOVNCL  = AsmCMOVcc(!32, ccNC  )
asmCMOVNEL  = AsmCMOVcc(!32, ccNE  )
asmCMOVNGL  = AsmCMOVcc(!32, ccNG  )
asmCMOVNGEL = AsmCMOVcc(!32, ccNGE )
asmCMOVNLL  = AsmCMOVcc(!32, ccNL  )
asmCMOVNLEL = AsmCMOVcc(!32, ccNLE )
asmCMOVNOL  = AsmCMOVcc(!32, ccNO  )
asmCMOVNPL  = AsmCMOVcc(!32, ccNP  )
asmCMOVNSL  = AsmCMOVcc(!32, ccNS  )
asmCMOVNZL  = AsmCMOVcc(!32, ccNZ  )
asmCMOVOL   = AsmCMOVcc(!32, ccO   )
asmCMOVPL   = AsmCMOVcc(!32, ccP   )
asmCMOVPEL  = AsmCMOVcc(!32, ccPE  )
asmCMOVPOL  = AsmCMOVcc(!32, ccPO  )
asmCMOVSL   = AsmCMOVcc(!32, ccS   )
asmCMOVZL   = AsmCMOVcc(!32, ccZ   )


AsmPUSH(size) =
	[src] -> [
		Assign(<Word(size)>,<Reg(!"esp")>,
			Binary(Minus(<Word(size)>),<Reg(!"esp")>,Lit(<Word(size)>,4))),
		Assign(<Word(size)>,Ref(<Reg(!"esp")>),src)
	]

asmPUSHW = AsmPUSH(!8)
asmPUSHL = AsmPUSH(!16)


AsmPOP(size) =
	[dst] -> [
		Assign(<Word(size)>,dst,Ref(<Reg(!"esp")>)),
		Assign(<Word(size)>,<Reg(!"esp")>,
			Binary(Plus(<Word(size)>),<Reg(!"esp")>,Lit(<Word(size)>,4)))
	]

asmPOPW = AsmPOP(!8)
asmPOPL = AsmPOP(!16)

''')


