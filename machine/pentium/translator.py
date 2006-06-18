'''Module for handling assembly language code.'''


import transf

import ir.transfs

from ssl.pentium import insn_table


sslTranslationTable = {
	"orl": "OR.RMOD",
	"xorl": "XOR.RMOD",
	"leal": "LEA.OD",
	"imull": "IMUL.OD",
	"pushl": "PUSH.OD",
	"popl": "POP.OD",
	"leave": "LEAVE",
}


class SslLookup(transf.base.Transformation):

	tmp_no = 0
	
	def __init__(self):
		transf.base.Transformation.__init__(self)

	def apply(self, term, ctx):
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
			kargs[temp] = term.factory.make("Sym(_)", name)

		return term.factory.make(pattern, **kargs)	


simplifyExpr = transf.parse.Rule('''
	BitNot(1) -> Not
|	BitOr(1) -> Or
|	BitAnd(1) -> And
''')

simplifyStmt = transf.parse.Rule('''
	Assign(type, dst, Cond(cond, src, dst))
		-> If(cond, Assign(type, dst, src), NoStmt)
	
|	Assign(type, dst, Cond(cond, src, dst))
		-> If(Unary(Not, cond), Assign(type, dst, src), NoStmt)
		
|	Assign(_, Sym("pc"), expr)
		-> Branch(Addr(expr))

|	Cond(cond,Lit(Int(_,_),1),Lit(Int(_,_),0))
		-> cond
|	Cond(cond,Lit(Int(_,_),0),Lit(Int(_,_),1))
		-> Not(cond)

|	Ref(Addr(expr))
		-> expr
|	Addr(Ref(expr))
		-> expr
''')

simplify = transf.traverse.InnerMost(simplifyExpr | simplifyStmt)

sslLookup = SslLookup() & simplify
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

declReg32 = !VarDef(Int(32,Unknown),<id>,NoExpr)
declFlag = !VarDef(Bool,<id>,NoExpr)

stmtsPreambule =
	concat(
		reg32Names ; map(declReg32) ; debug.Dump(),
		flagNames ; map(declFlag)
	)

''')

stmts = transf.base.Proxy()

doStmt = transf.parse.Rule('''
	Asm("ret", [])
		-> [Ret(Void, NoExpr)]
|	Asm("call", [Ref(addr)])
		-> [Assign(Void, NoExpr, Call(addr,[]))]
|	Asm	
		-> <sslLookup>
|	_ 
		-> [_]
''')

stmt = ir.traverse.Stmt(
	stmts=stmts, 
	Wrapper = ir.traverse.UP(doStmt)
)

stmts.subject = transf.traverse.Map(stmt) & transf.lists.concat

#stmts.subject = transf.debug.Trace('stmts', stmts.subject)
#stmt.subject = transf.debug.Trace('stmt', stmt.subject)

module = ir.traverse.Module(
	stmts = transf.lists.Concat2(transf.debug.Dump() & stmtsPreambule, stmts), 
)


