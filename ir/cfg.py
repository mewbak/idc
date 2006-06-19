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
		+((matchModule + matchStmt) * setStmtId),
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


setLabelTable = util.Proxy()
setLabelTables = lists.Map(setLabelTable)
setLabelTable.subject = parse.Transf('''
	Where(
		setLabelRef +
		reduceStmts ;
		setLabelTables
	)
''')

LabelTable = lambda operand: scope.Local2(
	(
		('lbls', table.Table),
	),
	setLabelTable * operand,
)

LookupLabel = lambda name: name * table.Get('lbls')


#######################################################################
# Statements Flow

ctrlFlowAnno = 'CtrlFlow'

getCtrlFlow = annotation.Get(ctrlFlowAnno)
SetCtrlFlow = lambda flows: annotation.Set(ctrlFlowAnno, flows)


#######################################################################
# Flow Traversal

GetTerminalNodeId = lambda id: arith.NegInt(id)

markStmtFlow = util.Proxy()
markStmtsFlow = util.Proxy()

markStmtFlow.subject = parse.Transf('''
let this = getStmtId in
	?Assign
		< SetCtrlFlow(![next])
		; !this => next
+	?Label
		< SetCtrlFlow(![next])
		; !this => next
+	?Asm 
		< SetCtrlFlow(![next])
		; !this => next
+	?If
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; !next => true end>, 
				<let next=!next in markStmtFlow; !next => false end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; !this => next
+	?While
		< { true, false:
			!next => false
			; ~_(_, <markStmtsFlow; !next => true>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; !this => next
+	?NoStmt
		< SetCtrlFlow(![next])
		; !this => next
+	?Continue 
		< SetCtrlFlow(![cont])
		; !this => next
+	?Break 
		< SetCtrlFlow(![brek])
		; !this => next
+	?Ret 
		< SetCtrlFlow(![retn])
		; !this => next
+	?Jump
		< SetCtrlFlow({ _(Sym(name)) -> [<lists.Lookup(!name,!lbls)>] } + ![])
		; !this => next
+	?Block
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; !this => next
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
		# !next => next
+	
		SetCtrlFlow({ n(*) -> [next{Cond(n)}] })
		; !this => next
end
''')

markStmtFlow.subject = parse.Transf('''
let this = getStmtId in
	?Assign
		< SetCtrlFlow(![next])
		; !this => next
+	?Label
		< SetCtrlFlow(![next])
		; !this => next
+	?Asm 
		< SetCtrlFlow(![next])
		; !this => next
+	?If
		< { true, false: 
			~_(_, 
				<let next=!next in markStmtFlow; !next => true end>, 
				<let next=!next in markStmtFlow; !next => false end>
			)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}]) 
		}
		; !this => next
+	?While
		< { true, false:
			!next => false
			; ~_(_, <markStmtsFlow; !next => true>)
			; SetCtrlFlow(![true{Cond("True")}, false{Cond("False")}])
		}
		; !this => next
+	?NoStmt
		< SetCtrlFlow(![next])
		; !this => next
+	?Continue 
		< SetCtrlFlow(![cont])
		; !this => next
+	?Break 
		< SetCtrlFlow(![brek])
		; !this => next
+	?Ret 
		< SetCtrlFlow(![retn])
		; !this => next
+	?Jump
		< SetCtrlFlow({ _(Sym(name)) -> [<LookupLabel(!name)>] } + ![])
		; !this => next
+	?Var
		< SetCtrlFlow(![next])
		; !this => next
+	?Block
		< ~_(<markStmtsFlow>)
		; SetCtrlFlow(![next])
		; !this => next
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
		# !next => next
+	
		SetCtrlFlow({ n(*) -> [next{Cond(n)}] })
		; !this => next
end
''')

markStmtsFlow.subject = lists.MapR(markStmtFlow)

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

markFlow = markStmtsIds * markModuleFlow


#######################################################################
# Graph Generation

makeNodeId = strings.tostr

makeAttr = lambda name, value: build._.Attr(name, value)

renderBox = \
	util.Adaptor(lambda term, ctx: term.factory.makeStr(box.stringify(term))) + \
	build.Str("???")

makeNodeLabel = parse.Rule('''
	If(cond,_,_)
		-> <<ir.pprint.expr>cond>
|	While(cond,_)
		-> <<ir.pprint.expr>cond>
|	_
		-> <ir.pprint.stmtKern>
|	n(*) 
		-> n
''') * renderBox * box.escape

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

makeNodeUrl = (path.get * box.reprz + build.empty ) * box.escape

makeNodeAttrs = \
	build.List([
		makeAttr("label", makeNodeLabel),
		makeAttr("shape", makeNodeShape),
		makeAttr("URL", makeNodeUrl),
	])

makeEdgeLabel = \
	annotation.Get('Cond') + \
	build.Str("")

makeEdgeAttrs = \
	build.List([
		makeAttr("label", makeEdgeLabel * box.escape),
	])

isValidNodeId = -match.zero

makeNodeEdges = \
	getCtrlFlow * \
	lists.Filter(
		build._.Edge(
			isValidNodeId * makeNodeId,
			makeEdgeAttrs,
		)
	)

makeNode = build._.Node(
	getStmtId * makeNodeId, 
	makeNodeAttrs, 
	makeNodeEdges
)

hasTerminalNode = match.Appl('Func', base.ident)

makeTerminalNode = hasTerminalNode * build._.Node(
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
	Node(src, <One(matchPointShapeAttr)>, [Edge(dst, _)]) -> [src, dst]
} ; =point

findPointNodes =
	Map(Try(findPointNode))

replaceEdge = 
	~Edge(<~point>, _)

removePointNode = 
	~Node(<Not(?point)>, _, <Map(Try(replaceEdge))>)

removePointNodes = 
	Filter(removePointNode)

simplifyPoints =
	with point[] in
		~Graph(<findPointNodes; removePointNodes>)
	end

''')

simplifyGraph = simplifyPoints


#######################################################################

render = markFlow * makeGraph * simplifyGraph

#######################################################################
# Example


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.factory
	for arg in sys.argv[1:]:
		print "* Reading aterm"
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( pprint2.module * renderBox )(term)
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
