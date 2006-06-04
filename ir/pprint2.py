'''Pretty-printing of intermediate representation code.
'''


from transf import *


def TraverseType(typer):
	typet = Proxy()
	typet.subject = ParseTransf('''
		~Int(_,_) +
		~Float(_) +
		~Char(size) +
		~Pointer(_, <typet>) +
		~Array(<typet>) +
		~Void
	''') & typer
	return typet


def TraverseExpr(exprr, typet, op):
	exprt = Proxy()
	exprt.subject = ParseTransf('''
		~False +
		~True +
		~Lit(<typet>, _) +
		~Sym(<id>) +
		~Cast(<typet>, <exprt>) +
		~Unary(<op>, <exprt>) +
		~Binary(<op>, <exprt>, <exprt>) +
		~Cond(<exprt>, <exprt>, <exprt>) +
		~Call(<exprt>, <map(exprt)>) +
		~Addr(<exprt>) +
		~Ref(<exprt>)
	''') & exprr
	return exprt


def TraverseStmt(stmtr, exprt, typet):
	stmtt = Proxy()
	stmtt.subject = ParseTransf('''
		~Assign(<typet>, <exprt>, <exprt>) +
		~Asm(_, <map(exprt)>) +
		~Label(_) +
		~Block(<map(stmtt)>) +
		~FuncDef(<typet>, _, _, <stmtt>) +
		~If(<exprt>, <stmtt>, <stmtt>) +
		~While(<exprt>, <stmtt>) +
		~Ret(<type>, <exprt>) +
		~Branch(label) +
		~Break +
		~Continue
	''') & stmtr
	return stmtt


def TraverseModule(moduler, stmtt):	
	modulet = ParseTransf('''
		~Module(<map(stmtt)>)
	''') & moduler
	return modulet
	


op = ParseTransf('''
	!T("type", "operator", <id>)
''')

kw = ParseTransf('''
	!T("type", "keyword", <id>)
''')

reprz = Adaptor(
	lambda term, context: term.factory.makeStr(repr(term.value))
)

print reprz("1")

lit = ParseTransf('''
	!T("type", "literal", <reprz>)
''')

sym = ParseTransf('''
	!T("type", "symbol", <id>)
''')

join = ParseTransf('''
	( ~[] + ~[_, *<foldr(?[], ![sep, <First()>, *<Second()>])>] );
	!H( <id> )
''')

commas = ParseTransf('''
	{ sep : where( !", " => sep ); join }
''')

sign = ParseRule('''
	Signed -> <<kw> "signed">
|	Unsigned -> <<kw> "unsigned">
''')

size = ParseRule('''
	8 -> <<kw> "char">
|	16 -> H([ <<kw> "short">, " ", <<kw> "int"> ])
|	32 -> <<kw> "int">
|	64 -> H([ <<kw> "long">, " ", <<kw> "int"> ])
|	n -> H([ "int", <<ToStr> n> ])
''')

typer = ParseRule('''
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
''')

op = ParseRule('''
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

exprr = ParseRule('''
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

exprr = ParseTransf('''
	!H([ "(", <exprr>, ")" ])
''')

stmtr = ParseRule('''
	Assign(type, dexpr, sexpr)
		-> H([ dexpr, " ", <<op> "=">, " ", sexpr, ";" ])
|	Asm(opcode, operands) 
		-> H([ <<kw>"asm">, "(", <<commas> [<<lit> opcode>, *operands]>, ")", ";" ])
|	Block(stmts)
		-> V([ "{", I(V( stmts )), "}" ])
|	FuncDef(type, name, args, body)
		-> D(V([
			H([ type, " ", name, "(", <<commas> args>, ")" ]),
			I( body )
		]))
|	Label(name)
		-> D(H([ name, ":" ]))
|	Ret(type,expr)
		-> H([ <<kw>"return">, " ", expr, ";"])
''')

moduler = ParseRule('''
	Module(stmts) -> V([ I(V( stmts )) ])
''')

type = TraverseType(typer)

expr = TraverseExpr(exprr, type, op)

stmt = TraverseStmt(stmtr, expr, type)

module = TraverseModule(moduler, stmt)


if __name__ == '__main__':
	import aterm.factory
	import box

	print commas('[1,2,3]')

	factory = aterm.factory.Factory()
	
	exprTestCases = [
		('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', '1 + x\n'),
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
	]
	
	for inputStr, output in stmtTestCases:
		input = factory.parse(inputStr)

		print input
		result = stmt(input)
		print result
		print box.box2text(result)
		print output
		print 
	
