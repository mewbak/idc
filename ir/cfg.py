'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *
from transf.exception import *
from transf.base import *
from transf.rewriters import *
from transf.grammar import *


from ir import pprint2


matchStmtName \
	= matching.MatchStr('VarDef') \
	| matching.MatchStr('FuncDef') \
	| matching.MatchStr('Assign') \
	| matching.MatchStr('If') \
	| matching.MatchStr('While') \
	| matching.MatchStr('Ret)') \
	| matching.MatchStr('Label') \
	| matching.MatchStr('Branch') \
	| matching.MatchStr('Block') \
	| matching.MatchStr('Break') \
	| matching.MatchStr('Continue') \
	| matching.MatchStr('NoOp') \
	| matching.MatchStr('Ret')


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
	return annotation.SetAnnotation(Build('Id'), Counter())


matchLabel = matching.MatchAppl(matching.MatchStr('Label'), combinators.Ident())

matchStmt = matching.MatchAppl(matchStmtName, combinators.Ident())

collectStmts = unifiers.CollectAll(matchStmt)

markStmts = traversal.TopDown(combinators.Try(matchStmt & AnnotateId()))



this = building.BuildVar("this")
next = building.BuildVar("next")
cont = building.BuildVar("cont")
brek = building.BuildVar("brek")
retn = building.BuildVar("retn")


def Edge(src, dst):
	return building.BuildList((src, dst))


stmtsFlow = base.Proxy()

stmtFlow = ParseRule('''
	Assign(*) -> [[<id>,next]] |
	Label(*) -> [[<id>,next]] |
	NoOp(*) -> [[<id>,next]] |
	Ret(*) -> [[<id>,next]]
''')

stmtsFlow.subject \
	= scope.Scope(
			matching.MatchNil() \
				& building.BuildNil() \
			| matching.MatchCons(matching.MatchVar("head"), matching.MatchVar("tail") & (projection.Head() | building.BuildVar("next")) & matching.MatchVar("following")) \
				& lists.Concat(scope.With(building.BuildVar("head") & stmtFlow, next=building.BuildVar("following")), building.BuildVar("tail") & stmtsFlow)
		, ['head', 'tail', 'following'])


endOfModule = Build("NoStmt") & AnnotateId()

moduleEdges \
	= Match("Module(stmts)") \
		& scope.With(building.BuildVar("stmts") & stmtsFlow, next=endOfModule, cont=endOfModule, brek=endOfModule, retn=endOfModule)

	#| matching.MatchStr('Branch(label)') & building.BuildList((Edge(this,FindLabel(label)))) \
		#| Match("If(*,true,false)") & Concat(Concat(Build("[Edge(this,next)]", Build("[this, true, next]") & stmtsFlow), Build("[this, false, next]") & stmtsFlow)
		#| Match("While(*,block)") & Concat(Build("[Edge(this,next)]", Build("[this, next]") & stmtsFlow))
	#| matching.MatchStr('While') \
	#| matching.MatchStr('Label') \
	#| matching.MatchStr('Block') \
	#| matching.MatchStr('Break') \
	#| matching.MatchStr('Continue') \
	#| matching.MatchStr('Ret')


makeNodeId \
	= annotation.GetAnnotation(Build('Id')) & strings.ToStr()

box2text = base.Adaptor(
		lambda term, context: term.factory.makeStr(box.box2text(term))
)

makeNodeLabel = ParseTransf('''
		?Assign(*); pprint2.stmt; box2text +
		?Label(*); pprint2.stmt; box2text +
		?Ret(*); pprint2.stmt; box2text +
		?NoOp(*); !"" +
		! "..."
''')

makeNode = building.BuildAppl("Node", (makeNodeId, makeNodeLabel))
makeNodes = traversal.Map(makeNode)


makeEdge = ParseRule('''
	[src, dst] -> Edge(<<makeNodeId> src>, <<makeNodeId> dst>)
''')
makeEdges = traversal.Map(makeEdge)

collectFlows = moduleEdges

makeGraph = ParseTransf('''
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

makeDot = ParseRule(r'''
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

makeDot = traversal.BottomUp(makeDot)

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
