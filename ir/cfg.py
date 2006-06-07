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
|	If(_, true, false)
		-> <SetStmtFlows(!true, !false); ~_(_, <markStmtFlow>, <markStmtFlow>) >
|	NoStmt
		-> <SetStmtFlows(!next)>
|	Continue(*)
		-> <SetStmtFlows(!cont)>
|	Break(*)
		-> <SetStmtFlows(!brek)>
|	Ret(*)
		-> <SetStmtFlows(!retn)>
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

"""
markStmtsFlow.subject \
	= match.nil \
		build.List([base.ident, build._.next])
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

markStmtsFlow.subject = parse.Transf('''
	[] 
		-> [<id>,next]
|	[head, *tail]
		-> <
			<markStmtsFlow> tail => [new_tail, following];
			<{next: (next -> following); <markStmt> head}> head => new_head;
			![<new_head>,<new_tail>]
		>
''')"""

endOfModule = build._.NoStmt() & SetStmtId(build.Int(0)) & SetStmtFlows()

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
|	NoStmt
		-> ""
|	_ 
		-> "..."
''')

makeNodeShape = parse.Rule('''
	If(cond,_,_)
		-> "diamond"
|	NoStmt
		-> "point"
|	_ 
		-> "box"
''')

makeNodeEdges \
	= getStmtFlow \
	& traverse.Map(
		build._.Edge(makeNodeId)
	)

makeNodeAttr = lambda name, value: build._.Attr(name, value)

makeNodeAttrs \
	= build.List([
		makeNodeAttr("label", makeNodeLabel & box.escape),
		makeNodeAttr("shape", makeNodeShape)
	])

makeNode = build._.Node(
	getStmtId & makeNodeId, 
	makeNodeAttrs, 
	makeNodeEdges
)

makeNodes = build._[base.ident, endOfModule] & unify.CollectAll(makeNode)

makeGraph = build._.Graph(makeNodes)


#######################################################################
# Graph Simplification


CountSrcs = lambda id: unify.Count(match._.Edge(id, base.ident))
CountDsts = lambda id: unify.Count(match._.Edge(base.ident, id))




#######################################################################
# Dot output

dotAttr = parse.Rule('''
		Attr(name, value) 
			-> H([ name, "=", value ])
''')

dotAttrs = parse.Transf('''
		!H([ "[", <map(dotAttr); box.commas>, "]" ])
''')

dotNode = parse.Rule('''
		Node( nid, attrs, _)
			-> H([ nid, <<dotAttrs> attrs> ])
''')

dotNodes = traverse.Map(dotNode)

dotNodeEdge = parse.Rule('''
		Edge(dst) 
			-> H([ src, "->", dst ])
''')

dotNodeEdges = parse.Rule('''
		Node(src, _, edges) 
			-> <<map(dotNodeEdge)> edges>
''')

dotEdges = traverse.Map(dotNodeEdges) & lists.concat

makeDot = parse.Rule(r'''
		Graph(nodes)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( <<dotNodes> nodes> ),
				V( <<dotEdges> nodes> ),
				H([ "}" ])
			])

''')


#######################################################################
# Example


if __name__ == '__main__':
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))

		term = MarkStmtsIds() (term)
		#print term
		term = markFlow (term)
		print term
		print
		
		#print makeNodes (term)
		#print makeEdges (term)
		
		term = makeGraph(term)
		print term
		print
		
		term = makeDot(term)
		print term
		print

		dotcode = box.box2text(term)
		print dotcode

		import gtk
		import ui.dotview
		win = ui.dotview.DotView()
		win.set_dotcode(dotcode)
		gtk.main()

