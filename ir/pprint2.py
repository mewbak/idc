'''Pretty-printing of intermediate representation code.
'''


from transf import base
from transf import strings
from transf import parse
from transf import debug

import ir.traverse
from ir.traverse import UP, DOWN

from box import op
from box import kw
from box import lit
from box import sym
from box import commas


sign = parse.Rule('''
	Signed -> <<kw> "signed">
|	Unsigned -> <<kw> "unsigned">
''')

size = parse.Rule('''
	8 -> <<kw> "char">
|	16 -> H([ <<kw> "short">, " ", <<kw> "int"> ])
|	32 -> <<kw> "int">
|	64 -> H([ <<kw> "long">, " ", <<kw> "int"> ])
|	n -> H([ "int", <<strings.ToStr> n> ])
''')

typeUp = parse.Rule('''
	Int(size, sign)
		-> H([ <<sign> sign>, " ", <<size> size> ])
|	Float(32)
		-> <<kw> "float">
|	Float(64)
		-> <<kw> "double">
|	Char(size)
		-> <<kw> "char">
|	Pointer(size, type) 
		-> H([ type, " ", <<op> "*"> ])
|	Array(type)
		-> H([ type, "[", "]" ])
|	Void
		-> <<kw> "void">
|	Blob(size)
		-> H([ "blob", <<strings.ToStr> size> ])
|	_ -> "???"
''')

oper = parse.Rule('''
	Not -> "!"
|	BitNot(size) -> "~"
|	Neg(type) -> "-"

|	And -> "&&"
|	Or -> "||"
|	BitAnd(_) -> "&"
|	BitOr(_) -> "|"
|	BitXor(_) -> "^"
|	LShift(_) -> "<<"
|	RShift(_) -> ">>"
|	Plus(_) -> "+"
|	Minus(_) -> "-"
|	Mult(_) -> "*"
|	Div(_) -> "/"
|	Mod(_) -> "%"
|	Eq(_) -> "=="
|	NotEq(_) -> "!="
|	Lt(_) -> "<"
|	LtEq(_) -> "<="
|	Gt(_) -> ">"
|	GtEq(_) -> ">="
''')

exprUp = parse.Rule('''
	False 
		-> "FALSE"
|	True 
		-> "TRUE"
|	Lit(type, value)
		-> <<lit> value>
|	Sym(name)
		-> <<sym> name>
|	Cast(type, expr)
		-> H([ "(", type, ")", " ", expr ])
|	Unary(op, expr)
		-> H([ op, expr ])
|	Binary(op, lexpr, rexpr)
		-> H([ lexpr, " ", op, " ", rexpr ])
|	Cond(cond, texpr, fexpr)
		-> H([ cond, " ", <<op> "?">, " ", texpr, " ", <<op> ":">, " ", fexpr ])
|	Call(addr, args)
		-> H([ addr, "(", <<commas> args>, ")" ])
|	Addr(addr)
		-> H([ <<op> "&">, addr ])
|	Ref(expr)
		-> H([ <<op> "*">, expr ])
''')

exprUp = parse.Transf('''
	!H([ "(", <exprUp>, ")" ])
''')

stmtUp = parse.Rule('''
	Assign(type, dexpr, sexpr)
		-> H([ dexpr, " ", <<op> "=">, " ", sexpr, ";" ])
|	Asm(opcode, operands) 
		-> H([ <<kw>"asm">, "(", <<commas> [<<lit> opcode>, *operands]>, ")", ";" ])
|	If(cond, true, NoStmt)
		-> V([
				H([ <<kw>"if">, "(", cond, ")" ]),
				I( true )
		])
|	If(cond, true, false)
		-> V([
				H([ <<kw>"if">, "(", cond, ")" ]),
				I( true ),
				H([ <<kw>"else"> ]),
				I( true )
		])
|	While(cond, stmt)
		-> V([
			H([ <<kw>"while">, "(", cond, ")" ]),
			I(stmt)
		])
|	Block(stmts)
		-> V([ "{", I(V( stmts )), "}" ])
|	Branch(label)
		-> H([ <<kw>"goto">, " ", label, ";" ])
|	FuncDef(type, name, args, body)
		-> D(V([
			H([ type, " ", name, "(", <<commas> args>, ")" ]),
			I( body )
		]))
|	Label(name)
		-> D(H([ name, ":" ]))
|	Ret(type,NoExpr)
		-> H([ <<kw>"return">, ";"])
|	Ret(type,expr)
		-> H([ <<kw>"return">, " ", expr, ";"])
|	NoStmt
		-> _
''')

moduleUp = parse.Rule('''
	Module(stmts) -> V([ I(V( stmts )) ])
''')

if 0:
	oper = debug.Trace('oper', oper)
	exprUp = debug.Trace('exprUp', exprUp)
	stmtUp = debug.Trace('stmtUp', stmtUp)
	moduleUp = debug.Trace('moduleUp', moduleUp)


type = ir.traverse.Type(
	Wrapper = UP(typeUp)
)

expr = ir.traverse.Expr(
	type = type, 
	op = oper,
	Wrapper = UP(exprUp)
)

stmt = ir.traverse.Stmt(
	expr = expr,
	type = type,
	Wrapper = UP(stmtUp)
)

module = ir.traverse.Module(
	stmt = stmt,
	Wrapper = UP(moduleUp)
)


if __name__ == '__main__':
	import aterm.factory
	import box

	print commas('[1,2,3]')

	factory = aterm.factory.Factory()
	
	exprTestCases = [
		('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', '1 + x\n'),
		('Sym("eax"{Path,[0,1,1,0]}){Path,[1,1,0]}', ''),
		('Lit(Int(32{Path,[0,0,2,1,0]},Signed{Path,[1,0,2,1,0]}){Path,[0,2,1,0]},1234{Path,[1,2,1,0]}){Path,[2,1,0]}){Path,[1,0],Id,2}', '')
	]
	
	for inputStr, output in exprTestCases:
		input = factory.parse(inputStr)
			
		print input
		result = expr(inputStr)
		print result
		print box.box2text(result)
		print output
		print
		
	
	stmtTestCases = [
		('Label("label")', 'label:\n'),
		('Asm("ret",[])', 'asm("ret");\n'),
		('Asm("mov",[Sym("ax"), Lit(Int(32,Signed),1234)])', 'asm("mov", ax, 1234);\n'),
		('FuncDef(Void,"main",[],Block([]))', 'void main()\n{\n}\n'),	
		('Assign(Void,Sym("eax"{Path,[0,1,1,0]}){Path,[1,1,0]},Lit(Int(32{Path,[0,0,2,1,0]},Signed{Path,[1,0,2,1,0]}){Path,[0,2,1,0]},1234{Path,[1,2,1,0]}){Path,[2,1,0]}){Path,[1,0],Id,2}',''),
		('Assign(Blob(32{Path,[0,0,1,0]}){Path,[0,1,0]},Sym("eax"{Path,[0,1,1,0]}){Path,[1,1,0]},Lit(Int(32{Path,[0,0,2,1,0]},Signed{Path,[1,0,2,1,0]}){Path,[0,2,1,0]},1234{Path,[1,2,1,0]}){Path,[2,1,0]}){Path,[1,0],Id,2}',''),
		('If(Binary(Eq(Int(32,"Signed")),Binary(BitOr(32),Binary(BitXor(32),Sym("NF"),Sym("OF")),Sym("ZF")),Lit(Int(32,Signed),1)),Branch(Sym(".L4")),NoStmt)', ''),
	]
	
	for inputStr, output in stmtTestCases:
		input = factory.parse(inputStr)

		print input
		result = stmt(input)
		print result
		print box.box2text(result)
		print output
		print 
	
