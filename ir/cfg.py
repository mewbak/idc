'''Control Flow Graph (CFG) generation.'''


import aterm
import transf
import box

from transf import *

import ir.traverse
import ir.pprint
import lang.dot


#######################################################################
# Utilities

class Count(base.Transformation):

	def __init__(self, name):
		base.Transformation.__init__(self)
		self.name = name

	def apply(self, term, ctx):
		try:
			value = int(ctx[self.name])
		except TypeError:
			raise exception.Failure
		except KeyError:
			value = 0
		
		value += 1
		
		term = term.factory.makeInt(value)
		
		ctx[self.name] =  term
		return term


#######################################################################
# Statement matching

matchStmtName \
	= match.Str('VarDef') \
	| match.Str('FuncDef') \
	| match.Str('Assign') \
	| match.Str('Asm') \
	| match.Str('If') \
	| match.Str('While') \
	| match.Str('Ret)') \
	| match.Str('Label') \
	| match.Str('Branch') \
	| match.Str('Block') \
	| match.Str('Break') \
	| match.Str('Continue') \
	| match.Str('NoStmt') \
	| match.Str('Ret') \
	| match.Str('Module')

matchStmt = match.Appl(matchStmtName, base.ident)


#######################################################################
# Statements IDs

stmtIdAnno = 'StmtId'

getStmtId = annotation.Get(stmtIdAnno)
SetStmtId = lambda id: annotation.Set(stmtIdAnno, id)
setStmtId = SetStmtId(Count('stmtid'))

markStmtsIds = scope.Let(
	traverse.TopDown(combine.Try(matchStmt & setStmtId)),
	stmtid = build.zero
)



#######################################################################
# Branches & Labels

matchLabel = match.Appl(matchStmtName, base.ident)

makeLabelRef = parse.Rule('''
	Label(name) -> [name, <getStmtId>]
''')

makeLableTable = unify.CollectAll(matchLabel & makeLabelRef)
	

#######################################################################
# Statements Flow

ctrlFlowAnno = 'CtrlFlow'

getCtrlFlow = annotation.Get(ctrlFlowAnno)
SetCtrlFlow = lambda flows: annotation.Set(ctrlFlowAnno, flows)


#######################################################################
# Flow Traversal

setNext = scope.Set('next')
GetTerminalNodeId = lambda id: arith.NegInt(id)

markStmtFlow = base.Proxy()
markStmtsFlow = base.Proxy()

markStmtFlow.subject = parse.Transf('''
let this = getStmtId in
	?Assign(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Label(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Asm(*) 
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?If(*)
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; where(!next => true) end>, 
				<let next=!next in markStmtFlow; where(!next => false) end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; where(!this; setNext)
+	?While(*)
		< { true, false:
			where(!next => false)
			; ~_(_, <markStmtsFlow; where(!next => true)>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; where(!this; setNext)
+	?NoStmt(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Continue(*) 
		< SetCtrlFlow(![cont])
		; where(!this; setNext)
+	?Break(*) 
		< SetCtrlFlow(![brek])
		; where(!this; setNext)
+	?Ret(*) 
		< SetCtrlFlow(![retn])
		; where(!this; setNext)
+	?Branch(*)
		< SetCtrlFlow({ _(Sym(name)) -> [<lists.Lookup(!name,!lbls)>] } + ![])
		; where(!this; setNext)
+	?Block(*)
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; where(!this; setNext)
+	?FuncDef(*)
		< let 
			next = !next,
			retn = GetTerminalNodeId(!this),
			brek = !0,
			cont = !0,
			lbls = makeLableTable
		in 
			~_(_, _, _, <markStmtFlow>)
			; SetCtrlFlow(![next])
		end
		# where(!next; setNext)
+	
		SetCtrlFlow({ n(*) -> [next{Cond(n)}] })
		; where(!this; setNext)
end
''')

markStmtFlow.subject = parse.Transf('''
let this = getStmtId in
	?Assign(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Label(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Asm(*) 
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?If(*)
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; where(!next => true) end>, 
				<let next=!next in markStmtFlow; where(!next => false) end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; where(!this; setNext)
+	?While(*)
		< { true, false:
			where(!next => false)
			; ~_(_, <markStmtsFlow; where(!next => true)>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; where(!this; setNext)
+	?NoStmt(*)
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Continue(*) 
		< SetCtrlFlow(![cont])
		; where(!this; setNext)
+	?Break(*) 
		< SetCtrlFlow(![brek])
		; where(!this; setNext)
+	?Ret(*) 
		< SetCtrlFlow(![retn])
		; where(!this; setNext)
+	?Branch(*)
		< SetCtrlFlow({ _(Sym(name)) -> [<lists.Lookup(!name,!lbls)>] } + ![])
		; where(!this; setNext)
+	?Block(*)
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; where(!this; setNext)
+	?FuncDef(*)
		< let 
			next = !next,
			retn = GetTerminalNodeId(!this),
			brek = !0,
			cont = !0,
			lbls = makeLableTable
		in 
			~_(_, _, _, <markStmtFlow>)
			; SetCtrlFlow(![next])
		end
		# where(!next; setNext)
+	
		SetCtrlFlow({ n(*) -> [next{Cond(n)}] })
		; where(!this; setNext)
end
''')

def MapR(operand):
	map = base.Proxy()
	map.subject \
		= match.nil \
		| traverse.Cons(base.ident, map) \
		& traverse.Cons(operand, base.ident)
	return map

markStmtsFlow.subject = MapR(markStmtFlow)

markModuleFlow = parse.Transf('''
	?Module(*)
		; let
			next = !0,
			retn = !0,
			brek = !0,
			cont = !0,
			# TODO: don't make a global lable table
			lbls = makeLableTable
		in
			~_(<markStmtsFlow>)
		end
''')

if 0:
	markStmtFlow.subject = debug.Trace('markStmtFlow', markStmtFlow.subject)
	markStmtsFlow.subject = debug.Trace('markStmtsFlow', markStmtsFlow.subject)

markFlow = markStmtsIds & markModuleFlow


#######################################################################
# Graph Generation

makeNodeId = strings.ToStr()

makeAttr = lambda name, value: build._.Attr(name, value)

renderBox \
	= base.Adaptor(lambda term, ctx: term.factory.makeStr(box.stringify(term))) \
	| build.Str("???")

makeNodeLabel = parse.Rule('''
	If(cond,_,_)
		-> <<ir.pprint.expr>cond>
|	While(cond,_)
		-> <<ir.pprint.expr>cond>
|	_
		-> <ir.pprint.stmtKern>
|	n(*) 
		-> n
''') & renderBox

makeNodeShape = parse.Rule('''
	If(cond,_,_)
		-> "diamond"
|	While(cond,_)
		-> "diamond"
|	Module(*)
		-> "point"
|	Block(*)
		-> "point"
|	NoStmt
		-> "point"
|	_ 
		-> "box"
''')

makeNodeAttrs \
	= build.List([
		makeAttr("label", makeNodeLabel & box.escape),
		makeAttr("shape", makeNodeShape)
	])

makeEdgeLabel \
	= annotation.Get('Cond') \
	| build.Str("")

makeEdgeAttrs \
	= build.List([
		makeAttr("label", makeEdgeLabel & box.escape),
	])

isValidNodeId = combine.Not(match.zero)

makeNodeEdges \
	= getCtrlFlow \
	& traverse.Filter(
		build._.Edge(
			isValidNodeId & makeNodeId,
			makeEdgeAttrs,
		)
	)

makeNode = build._.Node(
	getStmtId & makeNodeId, 
	makeNodeAttrs, 
	makeNodeEdges
)

hasTerminalNode = match.Pattern('FuncDef(*)')

makeTerminalNode = hasTerminalNode & build._.Node(
	GetTerminalNodeId(getStmtId), 
	build.List([
		makeAttr("label", build.Str('""')),
		makeAttr("shape", build.Str("doublecircle")),
		makeAttr("style", build.Str("filled")),
		makeAttr("fillcolor", build.Str("black"))
	]),
	build.nil
)

reduceStmts = parse.Transf('''
{ stmts:
	( ?Block(stmts)
	+ ?If(_, *stmts)
	+ ?While(_, *stmts)
	+ ?FuncDef(_,_,_,*stmts)
	+ ?Module(stmts)
	) 
	; !stmts
	+ ![]
}
''')

# TODO: try to merge both collects in one? it doesn't seem to be more efficient though
makeNodes = lists.Concat(
	unify.CollectAll(makeNode, reduce = reduceStmts),
	unify.CollectAll(makeTerminalNode, reduce = reduceStmts)
)

makeGraph = build._.Graph(makeNodes)


#######################################################################
# Graph Simplification

matchPointShapeAttr = parse.Transf('''
	?Attr("shape", "point")
''')

matchPointShapeNode = parse.Rule('''
	Node(src, <one(matchPointShapeAttr)>, [Edge(dst, _)]) -> [src, dst]
''')

replaceEdge = parse.Transf('''
	~Edge(<?src;!dst>, _)
''')

removeInNode = parse.Transf('''
	~Node(<not(?src)>, _, <map(try(replaceEdge))>)
''')

removeInGraph = parse.Transf('''
	~Graph(<filter(removeInNode)>)
''')

collectPoints = unify.CollectAll(matchPointShapeNode)

def simplifyPoints(term, ctx):
		noStmts = collectPoints.apply(term, ctx)
		print noStmts
		for src, dst in noStmts:
			new_ctx = transf.context.Context(['src', 'dst'], ctx)
			new_ctx['src'] = src
			new_ctx['dst'] = dst
			print src, "INTO", dst
			term = removeInGraph.apply(term, new_ctx)
		return term

simplifyPoints = base.Adaptor(simplifyPoints)

simplifyGraph = simplifyPoints

#######################################################################

render = markFlow & makeGraph & simplifyGraph

#######################################################################
# Example


if __name__ == '__main__':
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))

		#print ( pprint2.module  )(term)
		#print ( pprint2.module & renderBox )(term)

		term = markStmtsIds (term)
		#print makeLableTable (term)
		#print (lists.Lookup(build.Str("main"), makeLableTable)) (term)
		#print term
		print
		#term = (debug.Traceback(markFlow)) (term)
		term = markFlow (term)
		#print term
		print
		
		print "*********"
		#print term
		print "*********"
		#sys.exit(0)
		
		#print makeNodes (term)
		#print makeEdges (term)
		
		term = makeGraph(term)
		print term
		print

		term = simplifyGraph (term)
		print term
		print
		
		dotcode = lang.dot.stringify(term)
		print dotcode

		import gtk
		import ui.dotview
		win = ui.dotview.DotWindow()
		win.set_dotcode(dotcode)
		win.connect('destroy', gtk.main_quit)
		gtk.main()

