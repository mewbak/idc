'''Module for handling assembly language code.'''


import transf

import ir.transfs

from ssl.pentium import insn_table


sslTranslationTable = {
	"orl": "OR.RMOD",
	"xorl": "XOR.RMOD",
	"leal": "LEA.OD",
	"imull": "IMUL.OD",
	"idivb": "IDIV",
	"idivw": "IDIV.AX",
	"idivl": "IDIV.EAX",
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


simplifyStmt = transf.parse.Rule('''
	Assign(type, dst, Cond(cond, src, dst))
		-> If(cond, Assign(type, dst, src), NoStmt)
	
|	Assign(type, dst, Cond(cond, src, dst))
		-> If(Unary(Bool,Not,cond), Assign(type, dst, src), NoStmt)
		
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

#simplify = transf.traverse.Map(transf.combine.Repeat(simplify))
simplify = transf.traverse.InnerMost(simplifyStmt)

sslLookup = SslLookup() & simplify
#sslLookup = transf.debug.Trace('sslLookup', sslLookup)

stmts = transf.base.Proxy()

doStmt = transf.parse.Rule('''
	Asm("ret", [])
		-> [Ret(Void, NoExpr)]
|	Asm(*)	
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
	stmts=stmts, 
)


