'''Module for handling assembly language code.'''


import sys

import transf.transformation
import transf.lib
import transf.parse

import ir.traverse
import ir.check

from lang.ssl.spec.pentium import insn_table


sslTranslationTable = {
	"cbtw": "CBW",
	"cwtl": "CWDE",
	"cwtd": "CWD",
	"cltd": "CDQ",
}


class SslLookup(transf.transformation.Transformation):

	tmp_no = 0

	def __init__(self):
		transf.transformation.Transformation.__init__(self)

	def apply(self, term, ctx):
		if not term.rmatch('Asm(_, [*])'):
			raise transf.exception.Failure

		opcode, operands = term.args

		sys.stderr.write("warning: looking up %s in SSL\n" % opcode)

		opcode = opcode.value
		try:
			opcode = sslTranslationTable[opcode]
		except KeyError:
			opcode = opcode.upper()

		try:
			params, temps, pattern = insn_table[opcode]
		except KeyError:
			raise transf.exception.Failure

		res = []
		kargs = {}
		for param, operand in zip(params, operands):
			kargs[param] = operand
		for temp in temps:
			self.tmp_no += 1
			name = "tmp%d" % self.tmp_no
			kargs[temp] = term.factory.make("Sym(_){Tmp}", name)

		return term.factory.make(pattern, **kargs)

sslLookup = SslLookup()
#sslLookup = transf.debug.Trace(sslLookup, 'sslLookup')


class Temp(transf.transformation.Transformation):
	"""Transformation which generates an unique temporary variable name."""

	tmp_no = 0

	def __init__(self):
		transf.transformation.Transformation.__init__(self)

	def apply(self, trm, ctx):
		self.tmp_no += 1
		name = "temp%d" % self.tmp_no
		return trm.factory.make("Sym(_){Tmp}", name)

temp =  Temp()


class OpcodeDispatch(transf.transformation.Transformation):
	"""Transformation to quickly dispatch the transformation to the appropriate
	transformation."""

	def __init__(self):
		transf.transformation.Transformation.__init__(self)

	def apply(self, trm, ctx):
		if not trm.rmatch('Asm(_, [*])'):
			raise transf.exception.Failure

		opcode, operands = trm.args

		opcode = opcode.value
		try:
			trf = eval("asm" + opcode.upper())
		except NameError:
			sys.stderr.write("warning: don't now how to translate opcode '%s'\n" % opcode)
			raise transf.exception.Failure

		return trf.apply(operands, ctx)


transf.parse.Transfs('''

simplifyExpr =
	Not(Int(1,_)) -> Not(Bool)
|	Or(Int(1,_)) -> Or(Bool)
|	And(Int(1,_)) -> And(Bool)


simplifyStmt = {
	Assign(type, dst, Cond(cond, src, dst))
		-> If(cond, Assign(type, dst, src), NoStmt)

|	Assign(type, dst, Cond(cond, src, dst))
		-> If(Unary(Not, cond), Assign(type, dst, src), NoStmt)

|	Assign(_, Sym("pc"), expr)
		-> GoTo(Addr(expr))

|	Cond(cond,Lit(Int(_,_),1),Lit(Int(_,_),0))
		-> cond
|	Cond(cond,Lit(Int(_,_),0),Lit(Int(_,_),1))
		-> Not(cond)

|	Ref(Addr(expr))
		-> expr
|	Addr(Ref(expr))
		-> expr
}

''')

simplify = transf.lib.traverse.InnerMost(simplifyExpr + simplifyStmt)


transf.parse.Transfs('''

reg32Names = ![
	"eax", "ebx", "ecx", "edx",
	"esi", "edi", "ebp", "esp"
]

reg16Names = ![
	"ax", "bx", "cx", "dx",
	"si", "di", "bp", "sp"
]

reg8Names = ![
	"ah", "bh", "ch", "dh",
	"al", "bl", "cl", "dl"
]

flagNames = ![
	"nf", "zf", "af", "pf",
	"cf", "of", "df", "if"
]

declReg32 = !Var(Int(32,NoSign),<id>,NoExpr)
declFlag = !Var(Bool,<id>,NoExpr)

stmtsPreambule =
	Concat(
		reg32Names ; Map(declReg32) ; debug.Dump(),
		flagNames ; Map(declFlag)
	)

Reg(reg) = !Sym(<reg>){Reg}
reg = !Sym(<id>){Reg}
typ = !Int(<id>,Unsigned)
lit = [size, value] -> Lit(<<typ>size>, value)
zer = [size] -> <<lit>[size, 0]>

af = Reg(!"af")
cf = Reg(!"cf")
sf = Reg(!"sf")
of = Reg(!"of")
pf = Reg(!"pf")
zf = Reg(!"zf")
nf = Reg(!"nf")
df = Reg(!"zf")

al = Reg(!"al")
ah = Reg(!"ah")
ax = Reg(!"ax")
dx = Reg(!"dx")
eax = Reg(!"eax")
edx = Reg(!"edx")

Word(size) =
	!Int(<size>,NoSign)
UWord(size) =
	!Int(<size>,Unsigned)
SWord(size) =
	!Int(<size>,Signed)

ZeroFlag(size, res) =
	!Assign(Bool, <<reg>"zf">, Binary(Eq(<Word(size)>), <res>, Lit(<Word(size)>,0)))

Negative(size, op) =
	!Binary(Lt(<SWord(size)>), <op>, Lit(<SWord(size)>,0))

NonNegative(size, op) =
	!Binary(GtEq(<SWord(size)>), <op>, Lit(<SWord(size)>,0))

NegativeFlag(size, res) =
	!Assign(Bool, <<reg>"nf">, <Negative(size, res)>)

HsbOne(size, op) =
	!Binary(RShift(<UWord(size)>),<op>,Lit(<UWord(size)>,<arith.DecInt(size)>))

HsbZero(size, op) =
	!Unary(Not(Bool),<HsbOne(size,op)>)

AddFlags(size, op1, op2, res) =
	![
		<ZeroFlag(size, res)>,
		<NegativeFlag(size, res)>,
		Assign(Bool, <<reg>"cf">,
			Binary(Or(Bool),
				Binary(And(Bool),<HsbOne(size,op1)>,<HsbOne(size,op2)>),
				Binary(And(Bool),
					<HsbZero(size,res)>,
					Binary(Or(Bool),<HsbOne(size,op1)>,<HsbOne(size,op2)>)
				)
			)
		),
		Assign(Bool, <<reg>"of">,
			Binary(Or(Bool),
				Binary(And(Bool),
					Binary(And(Bool),<Negative(size,op1)>,<Negative(size,op2)>),
					<NonNegative(size,res)>
				),
				Binary(And(Bool),
					Binary(And(Bool),<NonNegative(size,op1)>,<NonNegative(size,op2)>),
					<Negative(size,res)>
				)
			)
		)
	]

false = !Lit(Bool,0)
true = !Lit(Bool,1)

SubFlags(size, op1, op2, res) =
	![
		<ZeroFlag(size, res)>,
		<NegativeFlag(size, res)>,
		Assign(Bool, <<reg>"cf">,
			Binary(Or(Bool),
				Binary(And(Bool),<HsbZero(size,op1)>,<HsbOne(size,op2)>),
				Binary(And(Bool),
					<HsbZero(size,res)>,
					Binary(Or(Bool),<HsbZero(size,op1)>,<HsbOne(size,op2)>)
				)
			)
		),
		Assign(Bool, <<reg>"of">,
			Binary(Or(Bool),
				Binary(And(Bool),
					Binary(And(Bool),<NonNegative(size,op1)>,<Negative(size,op2)>),
					<NonNegative(size,res)>
				),
				Binary(And(Bool),
					Binary(And(Bool),<Negative(size,op1)>,<NonNegative(size,op2)>),
					<Negative(size,res)>
				)
			)
		)
	]

LogFlags(size,res) =
	![
		<ZeroFlag(size, res)>,
		<NegativeFlag(size, res)>,
		Assign(Bool, <<reg>"cf">, <false>),
		Assign(Bool, <<reg>"of">, <false>)
	]

AsmAdd(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Plus(type), dst, src)),
			*<AddFlags(size, !tmp, !src, !dst)>
		]
	end

asmADDB = AsmAdd(!8)
asmADDW = AsmAdd(!16)
asmADDL = AsmAdd(!32)

AsmSub(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Minus(type), dst, src)),
			*<SubFlags(size, !tmp, !src, !dst)>
		]
	end

asmSUBB = AsmSub(!8)
asmSUBW = AsmSub(!16)
asmSUBL = AsmSub(!32)

AsmInc(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Plus(type), dst, Lit(type,1))),
			*<AddFlags(size, !tmp, !Lit(type,1), !dst)>
		]
	end

asmINCB = AsmInc(!8)
asmINCW = AsmInc(!16)
asmINCL = AsmInc(!32)

AsmDec(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Minus(type), dst, Lit(type,1))),
			*<SubFlags(size, !tmp, !Lit(type,1), !dst)>
		]
	end

asmDECB = AsmDec(!8)
asmDECW = AsmDec(!16)
asmDECL = AsmDec(!32)

HighLow(size) =
	switch size
		case 8: ![<ah>,<al>]
		case 16: ![<dx>,<ax>]
		case 32: ![<edx>,<eax>]
	end

AsmMUL(size) =
	with
		type = Word(size),
		type2 = Word(arith.MulInt(size,!2)),
		tmp = temp
	in
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,low),Cast(type2,src))),
			Assign(type, low, Cast(type,tmp)),
			Assign(type, high, Cast(type,Binary(RShift(type),tmp,Lit(type2,<size>)))),
			Assign(Bool, <cf>, Binary(And(Bool),NotEq(type),high,Lit(type2,0))),
			Assign(Bool, <of>, Binary(And(Bool),NotEq(type),high,Lit(type2,0)))
		]>
	end

asmMULB = AsmMUL(!8)
asmMULW = AsmMUL(!16)
asmMULL = AsmMUL(!32)

AsmIMUL1(size,src) =
	with
		type = SWord(size),
		type2 = SWord(arith.MulInt(size,!2)),
		tmp = temp
	in
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,low),Cast(type2,<src>))),
			Assign(type, low, Cast(type,tmp)),
			Assign(type, high, Cast(type,Binary(RShift(type),tmp,Lit(type2,<size>)))),
			Assign(Bool, <cf>, Binary(And(Bool),Binary(NotEq(type),high,Lit(type2,0)),Binary(NotEq(type),high,Lit(type2,-1)))),
			Assign(Bool, <of>, Binary(And(Bool),Binary(NotEq(type),high,Lit(type2,0)),Binary(NotEq(type),high,Lit(type2,-1))))
		]
	end

AsmIMUL23(size,dst,src1,src2) =
	with
		type = SWord(size),
		type2 = SWord(arith.MulInt(size,!2)),
		tmp = temp
	in
		debug.Dump() ; ![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,<src1>),Cast(type2,<src2>))),
			Assign(type, <dst>, Binary(Mult(type),<src1>,<src2>)),
			Assign(Bool, <cf>, Binary(NotEq(type2),tmp,Cast(type2,<dst>))),
			Assign(Bool, <of>, Binary(NotEq(type2),tmp,Cast(type2,<dst>)))
		]
	end

AsmIMUL(size) =
	[op1] -> <AsmIMUL1(size,!op1)> |
	[op1,op2] -> <AsmIMUL23(size,!op1,!op1,!op2)> |
	[op1,op2,op3] -> <AsmIMUL23(size,!op1,!op2,!op3)>

asmIMULB = AsmIMUL(!8)
asmIMULW = AsmIMUL(!16)
asmIMULL = AsmIMUL(!32)

#FIXME: handle 8 bit specially

AsmDIV(size) =
	with
		type = Word(size),
		type2 = Word(arith.MulInt(size,!2)),
		tmp1 = temp,
		tmp2 = temp
	in
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp1,
				Binary(And(type2),
					Cast(type2,low),
					LShift(type2,Cast(type2,high),Lit(type2,<size>))
				)
			),
			Assign(type, tmp2, src),
			Assign(type, low, Cast(type,Binary(Div(type2),tmp1,Cast(type2,tmp2)))),
			Assign(type, high, Cast(type,Binary(Mod(type2),tmp1,Cast(type2,tmp2))))
			# FIXME: undefine flags
		]>
	end

asmDIVB = AsmDIV(!8)
asmDIVW = AsmDIV(!16)
asmDIVL = AsmDIV(!32)

AsmIDIV(size) =
	with
		type = SWord(size),
		type2 = SWord(arith.MulInt(size,!2)),
		tmp1 = temp,
		tmp2 = temp
	in
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp1,
				Binary(And(type2),
					Cast(type2,low),
					Binary(LShift(type2),Cast(type2,high),Lit(type2,<size>))
				)
			),
			Assign(type, tmp2, src),
			Assign(type, low, Cast(type,Binary(Div(type2),tmp1,Cast(type2,tmp2)))),
			Assign(type, high, Cast(type,Binary(Mod(type2),tmp1,Cast(type2,tmp2))))
			# FIXME: undefine flags
		]>
	end

asmIDIVB = AsmIDIV(!8)
asmIDIVW = AsmIDIV(!16)
asmIDIVL = AsmIDIV(!32)

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

#AsmSAx(size, dir, dst, src) =
#	with
#		type = Word(size),
#		tmp = temp
#	in
#		![
#			Assign(type, tmp, src), Binary(dir(type),dst, src)
#			Assign(type, tmp, Binary(And(type), dst, src)),
#			*<LogFlags(size, !tmp)>
#		]
#	end
#	[Assign(
#	[dst,src] -> [
#		Assign(<Word(size)>, dst, Binary(<op>,dst,src)),
#		*<LogFlags(size, !dst)>
#	]


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

AsmCmp(size) =
	with
		type = Word(size),
		tmp = temp
	in
		[dst, src] -> [
			Assign(type, tmp, Binary(Minus(type), dst, src)),
			*<SubFlags(size, !dst, !src, !tmp)>
		]
	end

asmCMPB = AsmCmp(!8)
asmCMPW = AsmCmp(!16)
asmCMPL = AsmCmp(!32)

AsmMOV(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,src)]

asmMOVB = AsmMOV(!8)
asmMOVW = AsmMOV(!16)
asmMOVL = AsmMOV(!32)

AsmLEA(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,Addr(src))]

asmLEAW = AsmLEA(!8)
asmLEAL = AsmLEA(!16)

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

asmCLTD =
	[] -> [Assign(Bool,<df>,Lit(Bool,0))]

# FIXME:
asmREP =
	[] -> ![]

asmJMP =
	[Ref(addr)] -> [GoTo(addr)]

AsmJcc(cond) =
	[Ref(addr)] -> [If(<cond>,GoTo(addr),NoStmt)]

LNot(op1) = !Unary(Not(Bool),<op1>)
LAnd(op1,op2) = !Binary(And(Bool),<op1>,<op2>)
LOr(op1,op2) = !Binary(Or(Bool),<op1>,<op2>)
LEq(op1,op2) = !Binary(Eq(Bool),<op1>,<op2>)
LNotEq(op1,op2) = !Binary(NotEq(Bool),<op1>,<op2>)

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

doStmt =
	?Asm(opcode, _) < (
		OpcodeDispatch() +
		![<id>]
	) ;
	Try(simplify)
+	![<id>]


''', verbose=False)

module = ir.traverse.Module(
	stmts = transf.lib.lists.MapConcat(doStmt),
) #* ir.check.module


