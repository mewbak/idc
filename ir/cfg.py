'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *
from transf.exception import *
from transf.base import *
from transf.rewrite import *


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
	| match.Str('NoOp') \
	| match.Str('Ret')


class Counter(Transformation):

	def __init__(self):
		Transformation.__init__(self)
		self.last = 0

	def apply(self, term, context):
		self.last += 1
		return term.factory.makeInt(self.last)

	def reset(self):
		self.last = 0


def AnnotateId():
	return annotation.SetAnnotation(build.Pattern('Id'), Counter())


matchLabel = match.Appl(match.Str('Label'), base.Ident())

matchStmt = match.Appl(matchStmtName, base.Ident())

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

stmtFlow = parse.Rule('''
	Assign(*) -> [[<id>,next]] |
	Label(*) -> [[<id>,next]] |
	NoOp(*) -> [[<id>,next]] |
	Ret(*) -> [[<id>,next]]
''')

stmtsFlow.subject \
	= scope.Scope(
			match.Nil() \
				& build.Nil() \
			| match.Cons(match.Var("head"), match.Var("tail") & (project.Head() | build.Var("next")) & match.Var("following")) \
				& lists.Concat(scope.With(build.Var("head") & stmtFlow, next=build.Var("following")), build.Var("tail") & stmtsFlow)
		, ['head', 'tail', 'following'])


endOfModule = build.Pattern("NoStmt") & AnnotateId()

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
	= annotation.GetAnnotation(build.Pattern('Id')) & strings.ToStr()

box2text = base.Adaptor(
		lambda term, context: term.factory.makeStr(box.box2text(term))
)

makeNodeLabel = parse.Transf('''
		?Assign(*); pprint2.stmt; box2text +
		?Label(*); pprint2.stmt; box2text +
		?Ret(*); pprint2.stmt; box2text +
		?NoOp(*); !"" +
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


def escapes(s):
	s = s.replace('\"', '\\"')
	s = s.replace('\t', '\\t')
	s = s.replace('\r', '\\r')
	s = s.replace('\n', '\\n')
	return '"' + s + '"'

escape = Adaptor(
		lambda term, context: term.factory.makeStr(escapes(term.value))
)

makeDot = parse.Rule(r'''
		Graph(nodes, edges)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( nodes ),
				V( edges ),
				H([ "}" ])
			])
|		Node(nid, label) 
			-> H([ nid, "[", "label", "=", <<escape> label>, "]" ])
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

		term = makeGraph(term)
		print term
		
		term = makeDot(term)
		print term

		dotcode = box.box2text(term)
		print dotcode
		
		import os
		os.system("echo '%s' | dot -Tps | ggv - &" % dotcode)

		#term = markStmts.apply(term, {})

		#print ( collectStmts & makeNodes )(term)
		#print ( collectFlows & makeEdges )(term)
