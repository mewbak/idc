'''Control Flow Graph (CFG) generation.'''


import aterm
import transf
import box

from transf import *

from ir.common import *
import ir.traverse
import ir.pprint
import lang.dot


#######################################################################
# Statements IDs

stmtIdAnno = 'StmtId'

getStmtId = annotation.Get(stmtIdAnno)
setStmtId = annotation.Set(stmtIdAnno, arith.Count('stmtid'))

markStmtsIds = scope.Let2((
		('stmtid', build.zero),
	),
	traverse.TopDown(
		combine.Try((matchModule | matchStmt) & setStmtId),
		stop = stopStmts
	),
)


#######################################################################
# Jumpes & Labels

makeLabelRef = parse.Rule('''
	Label(name) -> [name, <getStmtId>]
''')

makeLabelTable = unify.CollectAll(makeLabelRef)

setLabelRef = parse.Transf('''
	{Label(name) -> [name, <getStmtId>] } ; =lbls
''')


setLabelTable = base.Proxy()
setLabelTables = traverse.Map(setLabelTable)
setLabelTable.subject = parse.Transf('''
	where(
		setLabelRef
		+ reduceStmts
		; setLabelTables
	)
''')

LabelTable = lambda operand: scope.Local2(
	(
		('lbls', table.Table),
	),
	setLabelTable & operand,
)

LookupLabel = lambda name: name & table.Get('lbls')


#######################################################################
# Statements Flow

ctrlFlowAnno = 'CtrlFlow'

getCtrlFlow = annotation.Get(ctrlFlowAnno)
SetCtrlFlow = lambda flows: annotation.Set(ctrlFlowAnno, flows)


#######################################################################
# Flow Traversal

setNext = variable.Set('next')
GetTerminalNodeId = lambda id: arith.NegInt(id)

markStmtFlow = base.Proxy()
markStmtsFlow = base.Proxy()

markStmtFlow.subject = parse.Transf('''
let this = getStmtId in
	?Assign
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Label
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Asm 
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?If
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; where(!next => true) end>, 
				<let next=!next in markStmtFlow; where(!next => false) end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; where(!this; setNext)
+	?While
		< { true, false:
			where(!next => false)
			; ~_(_, <markStmtsFlow; where(!next => true)>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; where(!this; setNext)
+	?NoStmt
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Continue 
		< SetCtrlFlow(![cont])
		; where(!this; setNext)
+	?Break 
		< SetCtrlFlow(![brek])
		; where(!this; setNext)
+	?Ret 
		< SetCtrlFlow(![retn])
		; where(!this; setNext)
+	?Jump
		< SetCtrlFlow({ _(Sym(name)) -> [<lists.Lookup(!name,!lbls)>] } + ![])
		; where(!this; setNext)
+	?Block
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Func
		< let 
			next = !next,
			retn = GetTerminalNodeId(!this),
			brek = !0,
			cont = !0
		in
			~_(_, _, _, <markStmtsFlow>)
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
	?Assign
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Label
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Asm 
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?If
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; where(!next => true) end>, 
				<let next=!next in markStmtFlow; where(!next => false) end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; where(!this; setNext)
+	?While
		< { true, false:
			where(!next => false)
			; ~_(_, <markStmtsFlow; where(!next => true)>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; where(!this; setNext)
+	?NoStmt
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Continue 
		< SetCtrlFlow(![cont])
		; where(!this; setNext)
+	?Break 
		< SetCtrlFlow(![brek])
		; where(!this; setNext)
+	?Ret 
		< SetCtrlFlow(![retn])
		; where(!this; setNext)
+	?Jump
		< SetCtrlFlow({ _(Sym(name)) -> [<LookupLabel(!name)>] } + ![])
		; where(!this; setNext)
+	?Var
		< SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Block
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; where(!this; setNext)
+	?Func
		< let 
			next = !next,
			retn = GetTerminalNodeId(!this),
			brek = !0,
			cont = !0
		in 
			LabelTable(~_(_, _, _, <markStmtsFlow>))
			; SetCtrlFlow(![next])
		end
		# where(!next; setNext)
+	
		SetCtrlFlow({ n(*) -> [next{Cond(n)}] })
		; where(!this; setNext)
end
''')

markStmtsFlow.subject = traverse.MapR(markStmtFlow)

markModuleFlow = parse.Transf('''
	?Module
		; let
			next = !0,
			retn = !0,
			brek = !0,
			cont = !0
		in
			LabelTable(~_(<markStmtsFlow>))
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
''') & renderBox & box.escape

makeNodeShape = parse.Rule('''
	If(cond,_,_)
		-> "diamond"
|	While(cond,_)
		-> "diamond"
|	Module
		-> "point"
|	Block
		-> "point"
|	NoStmt
		-> "point"
|	Var(_, _, NoExpr)
		-> "point"
|	_
		-> "box"
''')

makeNodeUrl = (path.get & box.reprz | build.empty ) & box.escape

makeNodeAttrs \
	= build.List([
		makeAttr("label", makeNodeLabel),
		makeAttr("shape", makeNodeShape),
		makeAttr("URL", makeNodeUrl),
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

hasTerminalNode = match.Appl('Func', base.ident)

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


# TODO: try to merge both collects in one? it doesn't seem to be more efficient though
makeNodes = lists.Concat(
	unify.CollectAll(makeNode, reduce = reduceStmts),
	unify.CollectAll(makeTerminalNode, reduce = reduceStmts)
)

makeGraph = build._.Graph(makeNodes)


#######################################################################
# Graph Simplification

parse.Transfs('''

matchPointShapeAttr = 
	?Attr("shape", "point")

findPointNode = {
	Node(src, <one(matchPointShapeAttr)>, [Edge(dst, _)]) -> [src, dst]
} ; =point

findPointNodes
	= map(try(findPointNode))

replaceEdge = 
	~Edge(<~point>, _)

removePointNode = 
	~Node(<not(?point)>, _, <map(try(replaceEdge))>)

removePointNodes = 
	filter(removePointNode)

simplifyPoints =
	with point[] in
		~Graph(<findPointNodes; removePointNodes>)
	end

''')

simplifyGraph = simplifyPoints


#######################################################################

render = markFlow & makeGraph & simplifyGraph

#######################################################################
# Example


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		print "* Reading aterm"
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( pprint2.module & renderBox )(term)
		#print

		print "* Marking statements"
		term = markStmtsIds (term)
		#print term
		#print
		
		print "* Marking flow"
		term = markFlow (term)
		#print term
		#print
		
		print "* Making Graph"
		term = makeGraph(term)
		#print term
		#print

		print "* Simplifying Graph"
		term = simplifyGraph (term)
		#print term
		#print
		
		print "* Generating DOT"
		term = simplifyGraph (term)
		dotcode = lang.dot.stringify(term)
		print dotcode

		import gtk
		import ui.dotview
		win = ui.dotview.DotWindow()
		win.set_dotcode(dotcode)
		win.connect('destroy', gtk.main_quit)
		gtk.main()


if __name__ == '__main__':
	main()
