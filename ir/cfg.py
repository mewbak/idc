'''Control Flow Graph (CFG) generation.'''


import aterm
import transf
from lang import box

from transf import lib
from transf import parse

import ir.traverse
import ir.pprint
import lang.dot


#######################################################################
# Graph Generation

renderBox = (
	lib.util.Adaptor(lambda term: term.factory.makeStr(box.stringify(term))) +
	lib.build.Str("???")
)

parse.Transfs(r"""

getNodeId =
	{ Label(label) -> label } < box.escape +
	Count('stmtid')

makeNodeLabel = {
	If(cond,_,_)
		-> <<ir.pprint.expr>cond>
|	While(cond,_)
		-> <<ir.pprint.expr>cond>
|	DoWhile(cond,_)
		-> <<ir.pprint.expr>cond>
|	_
		-> <ir.pprint.stmtKern>
|	n(*)
		-> n
} ; renderBox ; box.escape

makeNodeShape = {
	If
		-> "diamond"
|	While
		-> "diamond"
|	DoWhile
		-> "diamond"
|	Module
		-> "point"
|	Block
		-> "point"
|	NoStmt
		-> "point"
|	_
		-> "box"
}

makeNodeUrl =
	(path.get < box.reprz + build.empty ) ;
	box.escape

makeNodeAttrs =
	![
		!Attr("label", <makeNodeLabel>),
		!Attr("shape", <makeNodeShape>),
		!Attr("URL", <makeNodeUrl>)
	]

MakeEdge(dst) =
	!Edge(<dst>, [])
MakeLabelledEdge(dst, label) =
	!Edge(<dst>, [Attr("label", <label ; box.escape>)])

AddNode(nodeid, attrs, edges) =
	Where(
		!Node(
			<nodeid>,
			<attrs>,
			<edges>
		) ;
		![_,*nodes] ==> nodes
	)

GetTerminalNodeId(nodeid) =
	NegInt(nodeid)

hasTerminalNode =
	?Function

addTerminalNode =
	AddNode(
		!retn,
		![
			Attr("label", "\"\""),
			Attr("shape", "doublecircle"),
			Attr("style", "filled"),
			Attr("fillcolor", "black")
		],
		![]
	)
""")


#######################################################################
# Flow Traversal

parse.Transfs('''

doStmt =
	Proxy()

doStmts =
	MapR(doStmt)

MakeNode(edges) =
	AddNode(!this, makeNodeAttrs, edges)

doDefault =
	MakeNode(![<MakeEdge(!next)>]) ;
	!this ==> next

doIf =
	with true, false in
		?If(_,
			<with next=!next in doStmt; !next ==> true end>,
			<with next=!next in doStmt; !next ==> false end>
		) ;
		MakeNode(![
			<MakeLabelledEdge(!true, !"True")>,
			<MakeLabelledEdge(!false, !"False")>,
		]) ;
		! this ==> next
	end

doNoStmt =
	id

doWhile =
	with true in
		?While(_, <with next=!this in doStmt; !next ==> true end> );
		MakeNode(![
			<MakeLabelledEdge(!true, !"True")>,
			<MakeLabelledEdge(!next, !"False")>,
		]) ;
		! this ==> next
	end


doDoWhile =
	with false in
		! next ==> false ;
		! this ==> next ;
		?DoWhile(_, <doStmt> );
		MakeNode(![
			<MakeLabelledEdge(!next, !"True")>,
			<MakeLabelledEdge(!false, !"False")>,
		])
	end

doBreak =
	MakeNode(![<MakeEdge(!brek)>]) ;
	!this ==> next

doContinue =
	MakeNode(![<MakeEdge(!cont)>]) ;
	!this ==> next

doRet =
	MakeNode(![<MakeEdge(!retn)>]) ;
	!this ==> next

doGoTo =
	with
		label
	in
		?GoTo(Sym(label)) <
		MakeNode(![<MakeEdge(!label ; box.escape)>]) +
		MakeNode(![])
	end ;
	!this ==> next

doBlock =
	?Block(<doStmts>)

doFunction =
	with
		next = !next,
		retn = GetTerminalNodeId(!this),
		brek = !0,
		cont = !0
	in
		?Function(_, _, _, <doStmts>) ;
		MakeNode(![<MakeEdge(!next)>]) ;
		addTerminalNode
	end

doModule =
	with
		next = !0,
		retn = !0,
		brek = !0,
		cont = !0
	in
		?Module(<doStmts>) ;
		addTerminalNode
	end

doStmt.subject =
	debug.Dump() ;
	with
		this = getNodeId
	in
		switch project.name
		case "If": doIf
		case "While": doWhile
		case "DoWhile":	doDoWhile
		case "Break": doBreak
		case "GoTo": doGoTo
		case "Continue": doContinue
		case "NoStmt": doNoStmt
		case "Ret": doRet
		case "Block": doBlock
		case "Function": doFunction
		case "Module": doModule
		else doDefault
		end
	end

makeGraph =
	with
		nodes = ![],
		stmtid = !0
	in
		doModule ;
		AddNode(!"edge",![Attr("fontname","Arial")],![]) ;
		AddNode(!"node",![Attr("fontname","Arial")],![]) ;
		!Graph(nodes)
	end

''')


#######################################################################
# Graph Simplification

parse.Transfs('''

matchPointShapeAttr =
	?Attr("shape", "point")

findPointNode = {
	Node(src, <One(matchPointShapeAttr)>, [Edge(dst, _)]) -> [src, dst]
} ==> point

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

simplifyGraph = simplifyPoints
''')


#######################################################################

render = makeGraph * simplifyGraph

#######################################################################
# Example


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.factory
	for arg in sys.argv[1:]:
		print "* Reading aterm"
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( ir.pprint.module * renderBox )(term)
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

		#return

		import gtk
		import ui.dotview
		win = ui.dotview.DotWindow()
		win.set_dotcode(dotcode)
		win.connect('destroy', gtk.main_quit)
		gtk.main()


if __name__ == '__main__':
	main()
