'''Logical instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''

LogFlags(size,res) =
	![
		<ZeroFlag(size, res)>,
		<NegativeFlag(size, res)>,
		Assign(Bool, <cf>, <false>),
		Assign(Bool, <cf>, <false>)
	]

AsmLog(size, op) =
	[dst,src] -> [
		Assign(<Word(size)>, dst, Binary(<op>,dst,src)),
		*<LogFlags(size, !dst)>
	]

AsmAnd(size) = AsmLog(size, !And(<Word(size)>))
AsmOr(size) = AsmLog(size, !Or(<Word(size)>))
AsmXor(size) = AsmLog(size, !Xor(<Word(size)>))

asmANDB = AsmAnd(!8)
asmANDW = AsmAnd(!16)
asmANDL = AsmAnd(!32)

asmORB = AsmOr(!8)
asmORW = AsmOr(!16)
asmORL = AsmOr(!32)

asmXORB = AsmXor(!8)
asmXORW = AsmXor(!16)
asmXORL = AsmXor(!32)

AsmTest(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst, src] -> [
			Assign(type, tmp, Binary(And(type), dst, src)),
			*<LogFlags(size, !tmp)>
		]
	end

asmTESTB = AsmTest(!8)
asmTESTW = AsmTest(!16)
asmTESTL = AsmTest(!32)


''')

