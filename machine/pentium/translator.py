'''Module for handling assembly language code.'''


import transf.transformation
import transf.lib
import transf.parse

import ir.traverse


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

transf.parse.Transfs('''

simplifyExpr = {
	Not(Int(1,_)) -> Not(Bool)
|	Or(Int(1,_)) -> Or(Bool)
|	And(Int(1,_)) -> And(Bool)
}

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

sslLookup = SslLookup()
#sslLookup = transf.debug.Trace(sslLookup, 'sslLookup')

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

preStmt = {
	Asm("ret", [])
		-> Ret(Void, NoExpr)
|	Asm("rep", [])
		-> NoStmt
|	Asm("call", [Ref(addr)])
		-> Assign(Void, NoExpr, Call(addr,[]))
|	Asm("imull", [op1,op2])
		-> Asm("imull2", [op1,op2])
|	Asm("imull", [op1,op2,op3])
		-> Asm("imull3", [op1,op2,op3])
|	Asm("sarl", [op1])
		-> Asm("sarl", [op1,Lit(Int(32,Signed),1)])
}

doStmt =
	sslLookup + ![<id>]

''')

module = ir.traverse.Module(
	stmts = transf.lib.lists.MapConcat(+preStmt * doStmt * simplify),
)


