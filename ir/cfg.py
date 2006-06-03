'''Control Flow Graph (CFG) generation.'''

import aterm
import transf
import walker

from transf import *


class Grapher(walker.Walker):

	def __init__(self, factory, fp):
		walker.Walker.__init__(self, factory)
		self.fp = fp
		self.nodes = {}

	def graph(self, term):
		self.fp.write('digraph cfg {\n')
		self.collect()
		self.write_nodes()
		self.write_edges()
		self.fp.write('}\n')

	def collect_nodes(self, term):
		if self._match('Module(stmts)'):
			for stmt in stmts:
				collect_nodes(stmt)
		elif self._match(''):
			pass
	


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


matchFlowedStmtName \
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
	| MatchStr('NoOp')



class Counter(Transformation):

	def __init__(self):
		Transformation.__init__(self)
		self.last = 0

	def apply(self, term, context):
		self.last += 1
		return term.factory.makeInt(self.last)


def AnnotateId():
	return SetAnnotation(Build('Id'), Counter())


matchLabel = MatchAppl(MatchStr('Label'), Ident())

matchStmt = MatchAppl(matchStmtName, Ident())

matchNode = MatchAppl(matchStmtName & ~MatchStr('NoOp'), Ident())

collectNodes = CollectAll(matchNode)

markStmts = TopDown(Try(matchStmt & AnnotateId()))

nodeId \
	= GetAnnotation(Build('Id')) & ToStr()

nodeLabel \
	= Name()

node = BuildAppl("Node", (nodeId, nodeLabel))



this = BuildVar("this")
next = BuildVar("next")
cont = BuildVar("cont")
brek = BuildVar("brek")
retn = BuildVar("retn")

def Edge(src, dst):
	return BuildAppl("Edge", BuildList((src & nodeId, dst & nodeId)))

stmtsEdges = Proxy()

stmtEdges \
	=	Dump() & With(
			Match("Assign(*)") & BuildList((Edge(this,next),)) |
			Match("Label(*)") & BuildList((Edge(this,next),)) |
			Match("NoOp(*)") & BuildList((Edge(this,next),)) |
			Match("Ret(*)") & BuildList((Edge(this,next),)),
			this=Ident()
		)

stmtsEdges.subject \
	= Scope(
			MatchNil() \
				& BuildNil() \
			| MatchCons(MatchVar("head"), MatchVar("tail") & (Head() | BuildVar("next")) & MatchVar("following")) \
				& Concat(With(BuildVar("head") & stmtEdges, next=BuildVar("following")), BuildVar("tail") & stmtsEdges)
		, ['head', 'tail', 'following'])

endOfModule = Build("NoStmt") & AnnotateId()

moduleEdges \
	= Match("Module(stmts)") \
		& With(BuildVar("stmts") & stmtsEdges, next=endOfModule, cont=endOfModule, brek=endOfModule, retn=endOfModule)

	#| MatchStr('Branch(label)') & BuildList((Edge(this,FindLabel(label)))) \
		#| Match("If(*,true,false)") & Concat(Concat(Build("[Edge(this,next)]", Build("[this, true, next]") & stmtsEdges), Build("[this, false, next]") & stmtsEdges)
		#| Match("While(*,block)") & Concat(Build("[Edge(this,next)]", Build("[this, next]") & stmtsEdges))
	#| MatchStr('While') \
	#| MatchStr('Label') \
	#| MatchStr('Block') \
	#| MatchStr('Break') \
	#| MatchStr('Continue') \
	#| MatchStr('Ret')

edges = moduleEdges


if __name__ == '__main__':
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))
		term = markStmts.apply(term, {})
		#transf = CollectAll(matchLabel) & Map(node)
		transf = edges
		print transf.apply(term, {})

