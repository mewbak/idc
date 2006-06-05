'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *
from transf.exception import *
from transf.base import *
from transf.match import *
from transf.build import *
from transf.rewrite import *


from ir import pprint2


matchStmtName \
	= match.MatchStr('VarDef') \
	| match.MatchStr('FuncDef') \
	| match.MatchStr('Assign') \
	| match.MatchStr('If') \
	| match.MatchStr('While') \
	| match.MatchStr('Ret)') \
	| match.MatchStr('Label') \
	| match.MatchStr('Branch') \
	| match.MatchStr('Block') \
	| match.MatchStr('Break') \
	| match.MatchStr('Continue') \
	| match.MatchStr('NoOp') \
	| match.MatchStr('Ret')


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
	return annotation.SetAnnotation(BuildPattern('Id'), Counter())


matchLabel = match.MatchAppl(match.MatchStr('Label'), base.Ident())

matchStmt = match.MatchAppl(matchStmtName, base.Ident())

collectStmts = unify.CollectAll(matchStmt)

markStmts = traverse.TopDown(combine.Try(matchStmt & AnnotateId()))



this = build.BuildVar("this")
next = build.BuildVar("next")
cont = build.BuildVar("cont")
brek = build.BuildVar("brek")
retn = build.BuildVar("retn")


def Edge(src, dst):
	return build.BuildList((src, dst))


stmtsFlow = base.Proxy()

stmtFlow = parse.Rule('''
	Assign(*) -> [[<id>,next]] |
	Label(*) -> [[<id>,next]] |
	NoOp(*) -> [[<id>,next]] |
	Ret(*) -> [[<id>,next]]
''')

stmtsFlow.subject \
	= scope.Scope(
			match.MatchNil() \
				& build.BuildNil() \
			| match.MatchCons(match.MatchVar("head"), match.MatchVar("tail") & (project.Head() | build.BuildVar("next")) & match.MatchVar("following")) \
				& lists.Concat(scope.With(build.BuildVar("head") & stmtFlow, next=build.BuildVar("following")), build.BuildVar("tail") & stmtsFlow)
		, ['head', 'tail', 'following'])


endOfModule = BuildPattern("NoStmt") & AnnotateId()

moduleEdges \
	= MatchPattern("Module(stmts)") \
		& scope.With(build.BuildVar("stmts") & stmtsFlow, next=endOfModule, cont=endOfModule, brek=endOfModule, retn=endOfModule)

	#| match.MatchStr('Branch(label)') & build.BuildList((Edge(this,FindLabel(label)))) \
		#| MatchPattern("If(*,true,false)") & Concat(Concat(BuildPattern("[Edge(this,next)]", BuildPattern("[this, true, next]") & stmtsFlow), BuildPattern("[this, false, next]") & stmtsFlow)
		#| MatchPattern("While(*,block)") & Concat(BuildPattern("[Edge(this,next)]", BuildPattern("[this, next]") & stmtsFlow))
	#| match.MatchStr('While') \
	#| match.MatchStr('Label') \
	#| match.MatchStr('Block') \
	#| match.MatchStr('Break') \
	#| match.MatchStr('Continue') \
	#| match.MatchStr('Ret')


makeNodeId \
	= annotation.GetAnnotation(BuildPattern('Id')) & strings.ToStr()

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

makeNode = build.BuildAppl("Node", (makeNodeId, makeNodeLabel))
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
