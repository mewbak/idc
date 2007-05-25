'''Data transfer instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''

AsmMOV(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,src)]

asmMOVB = AsmMOV(!8)
asmMOVW = AsmMOV(!16)
asmMOVL = AsmMOV(!32)

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


