'''Pretty-printing of intermediate representation code.
'''


import math

from transf import *

from lang import box
from lang.box import op
from lang.box import kw
from lang.box import lit
from lang.box import sym
from lang.box import commas
from lang.box import Path


#######################################################################
# Int Literals

def _entropy(seq, states):
	state_freqs = dict.fromkeys(states, 0)
	for state in seq:
		state_freqs[state] += 1
	entropy = 0
	nstates = len(seq)
	for freq in state_freqs.itervalues():
		prob = float(freq)/nstates
		if prob:
			entropy -= prob*math.log(prob)
	return entropy

def intrepr(term, ctx):
	'''Represent integers, choosing the most suitable (lowest entropy) 
	representation.
	'''
	
	val = term.value

	d = "%d" % abs(val)
	x = "%x" % abs(val)
	sd = _entropy(d, "0123456789")
	sx = _entropy(x, "0123456789abcdef")
	if sx < sd:
		rep = hex(val)
	else:
		rep = str(val)
	
	return term.factory.makeStr(rep)
intrepr = util.Adaptor(intrepr)	

intlit = intrepr * box.const


#######################################################################
# Types

parse.Transfs('''
sign = {
	Signed -> H([ <<kw> "signed">, " " ])
|	Unsigned -> H([ <<kw> "unsigned"> , " " ])
|	NoSign -> ""
}

size = {
	8 -> <<kw> "char">
|	16 -> H([ <<kw> "short">, " ", <<kw> "int"> ])
|	32 -> <<kw> "int">
|	64 -> H([ <<kw> "long">, " ", <<kw> "int"> ])
|	n -> H([ "int", <<strings.tostr> n> ])
}

type = rec type : {
	Void
		-> <<kw> "void">
|	Bool
		-> <<kw> "bool">
|	Int(size, sign)
		-> H([ <<sign> sign>, <<size> size> ])
|	Float(32)
		-> <<kw> "float">
|	Float(64)
		-> <<kw> "double">
|	Char(size)
		-> <<kw> "char">
|	Pointer(size, type) 
		-> H([ <<type> type>, " ", <<op> "*"> ])
|	Array(type)
		-> H([ <<type> type>, "[", "]" ])
|	Blob(size)
		-> H([ "blob", <<strings.tostr> size> ])
|	_ -> "???"
}
''')

#######################################################################
# Operator precendence.
#
# See http://www.difranco.net/cop2220/op-prec.htm

unOpPrec = parse.Rule('''
	Not -> 1
|	Neg -> 1
''')

binOpPrec = parse.Rule('''
	And(Bool) -> 10 		
|	Or(Bool) -> 11 		
|	And(_) -> 7 		
|	Or(_) -> 9 		
|	Xor(_) -> 8 		
|	LShift -> 4 		
|	RShift -> 4 		
|	Plus -> 4 # force parenthesis inside shifts (was 3)
|	Minus -> 4 # force parenthesis inside shifts (was 3)
|	Mult -> 2 		
|	Div -> 2 		
|	Mod -> 2 		
|	Eq -> 6 
|	NotEq -> 6 
|	Lt -> 5 
|	LtEq -> 5 
|	Gt -> 5 
|	GtEq -> 5 	
''')

exprPrec = parse.Rule('''
	Lit(_, _) -> 0
|	Sym(_) -> 0
|	Cast(_, _) -> 1
|	Addr(_) -> 1
|	Ref(_) -> 1
|	Unary(op, _) -> <<unOpPrec>op>
|	Binary(op, _, _) -> <<binOpPrec>op>
|	Cond(_, _, _) -> 13
|	Call(_, _) -> 0
''')

stmtPrec = parse.Transf('''
	!99
''')

#######################################################################
# Expressions

unOp = parse.Rule('''
	Not(Bool) -> "!"
|	Not(_) -> "~"
|	Neg -> "-"
''')

binOp = parse.Rule('''
	And(Bool) -> "&&"
|	Or(Bool) -> "||"
|	And(_) -> "&"
|	Or(_) -> "|"
|	Xor(_) -> "^"
|	LShift -> "<<"
|	RShift -> ">>"
|	Plus -> "+"
|	Minus -> "-"
|	Mult -> "*"
|	Div -> "/"
|	Mod -> "%"
|	Eq -> "=="
|	NotEq -> "!="
|	Lt -> "<"
|	LtEq -> "<="
|	Gt -> ">"
|	GtEq -> ">="
''')

exprKern = util.Proxy()

parse.Transfs('''
SubExpr(Cmp) = 
	let 
		pprec = !prec, # parent precedence
		prec = exprPrec
	in
		if Cmp(!prec, !pprec) then
			!H([ "(", <exprKern>, ")" ])
		else
			exprKern
		end
	end

''')
subExpr = SubExpr(arith.Gt)
subExprEq = SubExpr(arith.Geq)

exprKern.subject = Path(parse.Rule('''
	Lit(Int(_,_), value)
		-> <<intlit> value>
|	Lit(type, value)
		-> <<lit> value>
|	Sym(name)
		-> <<sym> name>
|	Cast(type, expr)
		-> H([ "(", <<type>type>, ")", " ", <<subExpr>expr> ])
|	Unary(op, expr)
		-> H([ <<unOp>op>, <<subExpr>expr> ])
|	Binary(op, lexpr, rexpr)
		-> H([ <<subExpr>lexpr>, " ", <<binOp>op>, " ", <<subExprEq>rexpr> ])
|	Cond(cond, texpr, fexpr)
		-> H([ <<subExpr>cond>, " ", <<op>"?">, " ", <<subExpr>texpr>, " ", <<op>":">, " ", <<subExpr>fexpr> ])
|	Call(addr, args)
		-> H([ <<subExpr>addr>, "(", <<Map(subExpr);commas> args>, ")" ])
|	Addr(addr)
		-> H([ <<op>"&">, <<subExpr>addr> ])
|	Ref(expr)
		-> H([ <<op>"*">, <<subExpr>expr> ])
'''))

expr = parse.Transf('''
	let 
		prec = exprPrec
	in
		exprKern
	end
''')


#######################################################################
# Statements

stmt = util.Proxy()

stmts = parse.Transf('''
	!V( <Map(stmt)> ) 
''')

stmtKern = parse.Rule('''
	Assign(Void, NoExpr, src)
		-> H([ <<expr>src> ])
|	Assign(_, dst, src)
		-> H([ <<expr>dst>, " ", <<op>"=">, " ", <<expr>src> ])
|	If(cond, _, _)
		-> H([ <<kw>"if">, "(", <<expr>cond>, ")" ])
|	While(cond, _)
		-> H([ <<kw>"while">, "(", <<expr>cond>, ")" ])
|	Var(type, name, NoExpr)
		-> H([ <<type>type>, " ", name ])
|	Var(type, name, val)
		-> H([ <<type>type>, " ", name, "=", <<expr>val> ])
|	Function(type, name, args, stmts)
		-> H([ <<type>type>, " ", name, "(", <<commas> args>, ")" ])
|	Label(name)
		-> H([ name, ":" ])
|	GoTo(label)
		-> H([ <<kw>"goto">, " ", <<expr>label> ])
|	Ret(_, NoExpr)
		-> H([ <<kw>"return"> ])
|	Ret(_, value)
		-> H([ <<kw>"return">, " ", <<expr>value> ])
|	NoStmt
		-> ""
|	Asm(opcode, operands) 
		-> H([ <<kw>"asm">, "(", <<commas>[<<lit> opcode>, *<<Map(expr)>operands>]>, ")" ])
''')


parse.Transfs('''
ppLabel = {
	Label
		-> D( <stmtKern> )
}

ppBlock = {
	Block( stmts )
		-> V([
			D("{"), 
				<<stmts>stmts>, 
			D("}")
		])
}
		
ppIf = {
	If(_, true, NoStmt)
		-> V([
			<stmtKern>,
				I( <<stmt>true> )
		])
|	If(_, true, false)
		-> V([
			<stmtKern>,
				I( <<stmt>true> ),
			H([ <<kw>"else"> ]),
				I( <<stmt>false> )
		])
}

ppWhile = {
	While(_, body)
		-> V([
			<stmtKern>,
				I( <<stmt>body> )
		])
}

ppFunction = {
	Function(_, _, _, stmts)
		-> D(V([
			<stmtKern>, 
			"{",
				I(V([ <<stmts>stmts> ])),
			"}"
		]))
}

ppDefault =
	!H([ <stmtKern>, ";" ])

''')

stmt.subject = Path(parse.Transf('''
switch project.name
case "Label":
	ppLabel
case "Block":
	ppBlock
case "If":
	ppIf
case "While":
	ppWhile
case "Function":
	ppFunction
else:
	ppDefault
end
'''))

module = Path(parse.Rule('''
	Module(stmts)
		-> V([ 
			I( <<stmts>stmts> ) 
		])
'''))


#######################################################################
# Test


if __name__ == '__main__':
	import aterm.factory
	import box
	import check

	print commas('[1,2,3]')

	factory = aterm.factory.factory
	
	exprTestCases = [
		('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', '1 + x\n'),
		('Sym("eax"{Path([0,1,1,0])}){Path([1,1,0])}', ''),
		('Lit(Int(32{Path([0,0,2,1,0])},Signed{Path([1,0,2,1,0])}){Path([0,2,1,0])},1234{Path([1,2,1,0])}){Path([2,1,0])}){Path([1,0]),Id,2}', '')
	]
	
	for inputStr, output in exprTestCases:
		input = factory.parse(inputStr)
			
		print check.expr(input)
		result = expr(inputStr)
		print result
		print box.stringify(result)
		print output
		print
		
	
	stmtTestCases = [
		('Label("label")', 'label:\n'),
		('Asm("ret",[])', 'asm("ret");\n'),
		('Asm("mov",[Sym("ax"), Lit(Int(32,Signed),1234)])', 'asm("mov", ax, 1234);\n'),
		('Function(Void,"main",[],[])', 'void main()\n{\n}\n'),	
		('Assign(Void,Sym("eax"{Path([0,1,1,0])}){Path([1,1,0])},Lit(Int(32{Path([0,0,2,1,0])},Signed{Path([1,0,2,1,0])}){Path([0,2,1,0])},1234{Path([1,2,1,0])}){Path([2,1,0])}){Path([1,0]),Id,2}',''),
		('Assign(Blob(32{Path([0,0,1,0])}){Path([0,1,0])},Sym("eax"{Path([0,1,1,0])}){Path([1,1,0])},Lit(Int(32{Path([0,0,2,1,0])},Signed{Path([1,0,2,1,0])}){Path([0,2,1,0])},1234{Path([1,2,1,0])}){Path([2,1,0])}){Path([1,0]),Id,2}',''),
		('If(Binary(Eq(Int(32,Signed)),Binary(Or(Int(32,NoSign)),Binary(Xor(Int(32,NoSign)),Sym("NF"),Sym("OF")),Sym("ZF")),Lit(Int(32,Signed),1)),GoTo(Sym(".L4")),NoStmt)', ''),
	]
	
	for inputStr, output in stmtTestCases:
		input = factory.parse(inputStr)

		print input
		print check.stmt(input)
		result = stmt(input)
		print result
		print box.stringify(result)
		print output
		print 
	
