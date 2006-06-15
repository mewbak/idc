'''Pretty-printing of intermediate representation code.
'''


from transf import base
from transf import combine
from transf import strings
from transf import annotation
from transf import parse
from transf import debug

import ir.traverse
from ir.traverse import UP, DOWN

import box
from box import op
from box import kw
from box import lit
from box import sym
from box import commas


#######################################################################
# Path annotation

reprz = base.Adaptor(lambda term, ctx: term.factory.makeStr(str(term)))

Path = lambda operand: box.Tag('path', annotation.Get('Path') & reprz, operand ) | operand


#######################################################################
# Int Literals

import math
import sys

def entropy(seq, states):
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
	val = term.value

	d = "%d" % abs(val)
	x = "%x" % abs(val)
	sd = entropy(d, "0123456789")
	sx = entropy(x, "0123456789abcdef")
	if sx < sd:
		rep = hex(val)
	else:
		rep = str(val)
	
	return term.factory.makeStr(rep)
intrepr = base.Adaptor(intrepr)	

intlit = intrepr & box.const


#######################################################################
# Types

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

type = ir.traverse.Type(
	Wrapper = UP(typeUp)
)


#######################################################################
# Operator precendence.
#
# See http://www.difranco.net/cop2220/op-prec.htm

opPrec = parse.Rule('''
	Not(*) -> 1
|	BitNot(*) -> 1
|	Neg(*) -> 1
|	And(*) -> 10 		
|	Or(*) -> 11 		
|	BitAnd(*) -> 7 		
|	BitOr(*) -> 9 		
|	BitXor(*) -> 8 		
|	LShift(*) -> 4 		
|	RShift(*) -> 4 		
|	Plus(*) -> 3 		
|	Minus(*) -> 3 		
|	Mult(*) -> 2 		
|	Div(*) -> 2 		
|	Mod(*) -> 2 		
|	Eq(*) -> 6 
|	NotEq(*) -> 6 
|	Lt(*) -> 5 
|	LtEq(*) -> 5 
|	Gt(*) -> 5 
|	GtEq(*) -> 5 	
''')

exprPrec = parse.Rule('''
	False -> 0
|	True -> 0
|	Lit(_, _) -> 0
|	Sym(_) -> 0
|	Cast(_, _) -> 1
|	Addr(_) -> 1
|	Ref(_) -> 1
|	Unary(op, _) -> <<opPrec>op>
|	Binary(op, _, _) -> <<opPrec>op>
|	Cond(_, _, _) -> 13
|	Call(_, _) -> 0
''')


#######################################################################
# Expressions

oper = parse.Rule('''
	Not -> "!"
|	BitNot(_) -> "~"
|	Neg(_) -> "-"
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
|	Lit(_, value)
		-> <<intlit> value>
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
		-> H([ cond, " ", <<op>"?">, " ", texpr, " ", <<op>":">, " ", fexpr ])
|	Call(addr, args)
		-> H([ addr, "(", <<commas> args>, ")" ])
|	Addr(addr)
		-> H([ <<op>"&">, addr ])
|	Ref(expr)
		-> H([ <<op>"*">, expr ])
''')

Expr = lambda traverse: parse.Transf('''
	Path(
		let 
			pprec = !prec + !99, # parent precedence
			prec = exprPrec
		in
			traverse ;
			exprUp ;
			if gt(!prec, !pprec) then
				!H([ "(", <id>, ")" ])
				#!H([ "(GT:", <id>, ")" ])
			else
				id
				#!H([ "(LT:", <id>, ")" ])
			end
		end
	)
	''')

expr = ir.traverse.Expr(
	type = type, 
	op = oper,
	Wrapper = Expr
)


#######################################################################
# Statements

stmt = base.Proxy()

stmts = parse.Transf('''
	!V( <map(stmt)> ) 
''')

stmtKern = Path(parse.Rule('''
	Assign(Void, NoExpr, src)
		-> H([ <<expr>src> ])
|	Assign(_, dst, src)
		-> H([ <<expr>dst>, " ", <<op>"=">, " ", <<expr>src> ])
|	If(cond, _, _)
		-> H([ <<kw>"if">, "(", <<expr>cond>, ")" ])
|	While(cond, _)
		-> H([ <<kw>"while">, "(", <<expr>cond>, ")" ])
|	VarDef(type, name, NoExpr)
		-> H([ <<type>type>, " ", name ])
|	VarDef(type, name, val)
		-> H([ <<type>type>, " ", name, "=", <<expr>val> ])
|	FuncDef(type, name, args, body)
		-> H([ <<type>type>, " ", name, "(", <<commas> args>, ")" ])
|	Label(name)
		-> H([ name, ":" ])
|	Branch(label)
		-> H([ <<kw>"goto">, " ", <<expr>label> ])
|	Ret(_, NoExpr)
		-> H([ <<kw>"return"> ])
|	Ret(_, value)
		-> H([ <<kw>"return">, " ", <<expr>value> ])
|	NoStmt
		-> ""
|	Asm(opcode, operands) 
		-> H([ <<kw>"asm">, "(", <<commas>[<<lit> opcode>, *<<map(expr)>operands>]>, ")" ])
'''))

stmt.subject = Path(parse.Rule('''
	Assign(*)
		-> H([ <stmtKern>, ";" ])
|	If(_, true, NoStmt)
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
|	While(_, body)
		-> V([
			<stmtKern>,
				I( <<stmt>body> )
		])
|	Block( stmts )
		-> V([
			D("{"), 
				<<stmts>stmts>, 
			D("}")
		])
|	FuncDef(_, _, _, body)
		-> D(V([
			<stmtKern>,
				I( <<stmt>body> )
		]))
|	Label(*)
		-> D( <stmtKern> )
|	_
		-> H([ <stmtKern>, ";" ])
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

	factory = aterm.factory.Factory()
	
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
		('FuncDef(Void,"main",[],Block([]))', 'void main()\n{\n}\n'),	
		('Assign(Void,Sym("eax"{Path([0,1,1,0])}){Path([1,1,0])},Lit(Int(32{Path([0,0,2,1,0])},Signed{Path([1,0,2,1,0])}){Path([0,2,1,0])},1234{Path([1,2,1,0])}){Path([2,1,0])}){Path([1,0]),Id,2}',''),
		('Assign(Blob(32{Path([0,0,1,0])}){Path([0,1,0])},Sym("eax"{Path([0,1,1,0])}){Path([1,1,0])},Lit(Int(32{Path([0,0,2,1,0])},Signed{Path([1,0,2,1,0])}){Path([0,2,1,0])},1234{Path([1,2,1,0])}){Path([2,1,0])}){Path([1,0]),Id,2}',''),
		('If(Binary(Eq(Int(32,"Signed")),Binary(BitOr(32),Binary(BitXor(32),Sym("NF"),Sym("OF")),Sym("ZF")),Lit(Int(32,Signed),1)),Branch(Sym(".L4")),NoStmt)', ''),
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
	
