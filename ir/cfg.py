'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import box

from transf import *

from ir import pprint2


matchStmtName \
	= MatchStr('VarDef') \
	| MatchStr('FuncDef') \
	| MatchStr('Assign') \
	| MatchStr('If') \
	| MatchStr('While') \
	| MatchStr('Ret)') \
	| MatchStr('Label') \
	| MatchStr('Branch') \
	| MatchStr('Block') \
	| MatchStr('Break') \
	| MatchStr('Continue') \
	| MatchStr('NoOp') \
	| MatchStr('Ret')


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
	return SetAnnotation(Build('Id'), Counter())


matchLabel = MatchAppl(MatchStr('Label'), Ident())

matchStmt = MatchAppl(matchStmtName, Ident())

collectStmts = CollectAll(matchStmt)

markStmts = TopDown(Try(matchStmt & AnnotateId()))



this = BuildVar("this")
next = BuildVar("next")
cont = BuildVar("cont")
brek = BuildVar("brek")
retn = BuildVar("retn")


def Edge(src, dst):
	return BuildList((src, dst))


stmtsFlow = Proxy()

stmtFlow = ParseRule('''
	Assign(*) -> [[<id>,next]] |
	Label(*) -> [[<id>,next]] |
	NoOp(*) -> [[<id>,next]] |
	Ret(*) -> [[<id>,next]]
''')

stmtsFlow.subject \
	= Scope(
			MatchNil() \
				& BuildNil() \
			| MatchCons(MatchVar("head"), MatchVar("tail") & (Head() | BuildVar("next")) & MatchVar("following")) \
				& Concat(With(BuildVar("head") & stmtFlow, next=BuildVar("following")), BuildVar("tail") & stmtsFlow)
		, ['head', 'tail', 'following'])


endOfModule = Build("NoStmt") & AnnotateId()

moduleEdges \
	= Match("Module(stmts)") \
		& With(BuildVar("stmts") & stmtsFlow, next=endOfModule, cont=endOfModule, brek=endOfModule, retn=endOfModule)

	#| MatchStr('Branch(label)') & BuildList((Edge(this,FindLabel(label)))) \
		#| Match("If(*,true,false)") & Concat(Concat(Build("[Edge(this,next)]", Build("[this, true, next]") & stmtsFlow), Build("[this, false, next]") & stmtsFlow)
		#| Match("While(*,block)") & Concat(Build("[Edge(this,next)]", Build("[this, next]") & stmtsFlow))
	#| MatchStr('While') \
	#| MatchStr('Label') \
	#| MatchStr('Block') \
	#| MatchStr('Break') \
	#| MatchStr('Continue') \
	#| MatchStr('Ret')


makeNodeId \
	= GetAnnotation(Build('Id')) & ToStr()

box2text = Adaptor(
		lambda term, context: term.factory.makeStr(box.box2text(term))
)

makeNodeLabel = ParseTransf('''
		?Assign(*); pprint2.stmt; box2text +
		?Label(*); pprint2.stmt; box2text +
		?Ret(*); pprint2.stmt; box2text +
		?NoOp(*); !"" +
		! "..."
''')

makeNode = BuildAppl("Node", (makeNodeId, makeNodeLabel))
makeNodes = Map(makeNode)


makeEdge = ParseRule('''
	[src, dst] -> Edge(<<makeNodeId> src>, <<makeNodeId> dst>)
''')
makeEdges = Map(makeEdge)

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

makeDot = BottomUp(makeDot)

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
