'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *

from ir import pprint2


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


class Counter(base.Transformation):

	def __init__(self, value = 1):
		base.Transformation.__init__(self)
		self.value = value

	def apply(self, term, context):
		term = term.factory.makeInt(self.value)
		self.value += 1
		return term


def AnnotateId():
	return annotation.Set(build.Str('Id'), Counter())


matchLabel = match.Appl(match.Str('Label'), base.ident)

matchStmt = match.Appl(matchStmtName, base.ident)

collectStmts = unify.CollectAll(matchStmt)

markStmts = traverse.TopDown(combine.Try(matchStmt & AnnotateId()))



this = build.Var("this")
next = build.Var("next")
cont = build.Var("cont")
brek = build.Var("brek")
retn = build.Var("retn")


def Edge(src, dst):
	return build.List((src, dst))


stmtsFlow = base.Proxy()

stmtFlow = base.Proxy()
stmtFlow.subject = debug.Dump() & parse.Rule('''
	Assign(*) -> [[<id>,next]] |
	Label(_) -> [[<id>,next]] |
	If(_,true,NoStmt) -> <concat(![[<id>,next],[<id>,true]],<stmtFlow> true)> |
	If(_,true,false) -> <concat(![[<id>,true],[<id>,false]],<stmtFlow> true, <stmtFlow> false)> |
	NoStmt -> [[<id>,next]] |
	Ret(*) -> [[<id>,next]]
''')

stmtsFlow.subject \
	= scope.Scope(
			match.nil \
				& build.nil \
			| match.Cons(
				match.Var("head"), 
				match.Var("tail") & (project.head | build.Var("next")) & match.Var("following")
			) \
				& lists.Concat(
					scope.With(build.Var("head") & stmtFlow, next=build.Var("following")), 
					build.Var("tail") & stmtsFlow
				)
		, ['head', 'tail', 'following'])


endOfModule = build.Pattern("NoStmt{Id(0)}") 

moduleEdges \
	= match.Pattern("Module(stmts)") \
		& scope.With(build.Var("stmts") & stmtsFlow, next=endOfModule, cont=endOfModule, brek=endOfModule, retn=endOfModule)

	#| match.Str('Branch(label)') & build.List((Edge(this,FindLabel(label)))) \
		#| match.Pattern("If(*,true,false)") & Concat(Concat(build.Pattern("[Edge(this,next)]", build.Pattern("[this, true, next]") & stmtsFlow), build.Pattern("[this, false, next]") & stmtsFlow)
		#| match.Pattern("While(*,block)") & Concat(build.Pattern("[Edge(this,next)]", build.Pattern("[this, next]") & stmtsFlow))
	#| match.Str('While') \
	#| match.Str('Label') \
	#| match.Str('Block') \
	#| match.Str('Break') \
	#| match.Str('Continue') \
	#| match.Str('Ret')


makeNodeId \
	= annotation.Get(build.Str('Id')) & strings.ToStr()

box2text = base.Adaptor(
		lambda term, context: term.factory.makeStr(box.box2text(term))
)

makeNodeLabel = parse.Transf('''
		?Assign(*); pprint2.stmt; box2text +
		?Label(*); pprint2.stmt; box2text +
		?If(cond,_,_); <pprint2.expr> cond; box2text +
		?Ret(*); pprint2.stmt; box2text +
		?NoStmt(*); !"" +
		! "..."
''')

makeNode = build.Appl("Node", (makeNodeId, makeNodeLabel))
makeNodes = traverse.Map(makeNode)


makeEdge = parse.Rule('''
	[src, dst] -> Edge(<<makeNodeId> src>, <<makeNodeId> dst>)
''')
makeEdges = traverse.Map(makeEdge)

collectFlows = moduleEdges

makeGraph = parse.Transf('''
		markStmts;
		!Graph(<collectStmts; makeNodes>, <collectFlows; makeEdges>)
''')


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

		#print markStmts(term)
		#print ( markStmts & collectFlows & makeEdges )(term)
		#print ( markStmts & collectStmts & makeNodes )(term)

		term = makeGraph(term)
		print term
		
		term = makeDot(term)
		print term

		dotcode = box.box2text(term)
		print dotcode
		
		import os
		os.system("echo '%s' | dot -Tps | ggv - &" % dotcode)

