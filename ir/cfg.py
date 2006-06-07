'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *

from ir import pprint2



#######################################################################
# Utilities

class Counter(base.Transformation):

	def __init__(self, value = 1):
		base.Transformation.__init__(self)
		self.value = value

	def apply(self, term, context):
		term = term.factory.makeInt(self.value)
		self.value += 1
		return term


#######################################################################
# Statement matching

matchStmtName \
	= match.Str('VarDef') \
	| match.Str('FuncDef') \
	| match.Str('Assign') \
	| match.Str('If') \
	| match.Str('While') \
	| match.Str('Ret)') \
	| match.Str('Label') \
	| match.Str('Branch') \
	| match.Str('Block') \
	| match.Str('Break') \
	| match.Str('Continue') \
	| match.Str('NoStmt') \
	| match.Str('Ret')

matchStmt = match.Appl(matchStmtName, base.ident)


#######################################################################
# Statements IDs

stmtIdAnno = build.Str('StmtId')

getStmtId = annotation.Get(stmtIdAnno)
SetStmtId = lambda id: annotation.Set(stmtIdAnno, id)

MarkStmtsIds = lambda: traverse.TopDown(combine.Try(matchStmt & SetStmtId(Counter(1))))


#######################################################################
# Statements Flow

stmtFlowAnno = build.Str('StmtFlow')

getStmtFlow = annotation.Get(stmtFlowAnno)
SetStmtFlow = lambda flows: annotation.Set(stmtFlowAnno, flows)
SetStmtFlows = lambda *stmts: SetStmtFlow(build.List([stmt & getStmtId for stmt in stmts]))


#######################################################################
# Flow Traversal

markStmtsFlow = base.Proxy()

markStmtFlow = base.Proxy()

markStmtFlow.subject = parse.Rule('''
	Assign(*) 
		-> <SetStmtFlows(!next)>
|	Label(*) 
		-> <SetStmtFlows(!next)>
|	If(_, true, NoStmt) 
		-> <SetStmtFlows(!next, !true); ~_(_, <markStmtFlow>, _) >
|	If(_, true, false) 
		-> <SetStmtFlows(!true, !false); ~_(_, <markStmtFlow>, <markStmtFlow>) >
|	NoStmt
		-> <SetStmtFlows(!next)>
|	Ret(*)
		-> <SetStmtFlows(!next)>
''')

markStmtsFlow.subject \
	= match.nil \
	| scope.With(
		traverse.Cons(
			scope.With(
				markStmtFlow,
				next = build._.following
			),
			markStmtsFlow
		),
		following = project.tail & (project.head | build._.next)
	)

endOfModule = build._.NoStmt() & SetStmtId(build.Int(0))

markModuleFlow \
	= traverse._.Module( 
		scope.With(
				markStmtsFlow, 
				next=endOfModule, 
				cont=endOfModule, 
				brek=endOfModule, 
				retn=endOfModule
		)
	)

markFlow = markModuleFlow

MarkFlow = lambda: MarkStmtsIds() & markFlow


#######################################################################
# Graph Generation

makeNodeId = strings.ToStr()

renderBox = base.Adaptor(lambda term, context: term.factory.makeStr(box.box2text(term)))

makeNodeLabel = parse.Rule('''
	Assign(*)
		-> < pprint2.stmt; renderBox >
|	Label(*)
		-> < pprint2.stmt; renderBox >
|	If(cond,_,_)
		-> < <pprint2.expr> cond; renderBox >
|	Ret(*)
		-> < pprint2.stmt; renderBox >
|	NoStmt(*)
		-> ""
|	_ 
		-> "..."
''')

makeNode = build._.Node(getStmtId & makeNodeId, makeNodeLabel)
makeNodes = unify.CollectAll(makeNode)

makeNodeEdges = scope.With(
	getStmtFlow & traverse.Map(
		build._.Edge(build._.src, makeNodeId)
	),
	src = getStmtId & makeNodeId
)

makeEdges \
	= unify.CollectAll(makeNodeEdges) \
	& unify.Foldr(
	build.nil,
	lists.Concat
)

makeGraph = build._.Graph(makeNodes, makeEdges)


#######################################################################
# Dot output

makeDot = parse.Rule(r'''
		Graph(nodes, edges)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( nodes ),
				V( edges ),
				H([ "}" ])
			])
|		Node(nid, label) 
			-> H([ nid, "[", "label", "=", <<box.escape> label>, ",", "shape", "=", "box", "]" ])
|		Edge(src, dst) 
			-> H([ src, "->", dst ])
|		_ -> <id>
''')

makeDot = traverse.BottomUp(makeDot)



if __name__ == '__main__':
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))

		term = MarkStmtsIds() (term)
		print term
		term = markFlow (term)
		print term
		
		print makeNodes (term)
		print makeEdges (term)
		
		term = makeGraph(term)
		print term
		
		term = makeDot(term)
		print term

		dotcode = box.box2text(term)
		print dotcode

		import gtk
		import ui.dotview
		win = ui.dotview.DotView()
		win.set_dotcode(dotcode)
		gtk.main()

