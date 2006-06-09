'''Control Flow Graph (CFG) generation.'''


import aterm
import transf
import box

from transf import *

import ir.traverse
import ir.pprint
import lang.dot


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
	| match.Str('Asm') \
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

stmtIdAnno = 'StmtId'

getStmtId = annotation.Get(stmtIdAnno)
SetStmtId = lambda id: annotation.Set(stmtIdAnno, id)

MarkStmtsIds = lambda: traverse.TopDown(combine.Try(matchStmt & SetStmtId(Counter(1))))


#######################################################################
# Branches & Labels

matchLabel = match.Appl(matchStmtName, base.ident)

makeLabelRef = parse.Rule('''
	Label(name) -> [name, <getStmtId>]
''')

makeLableTable = unify.CollectAll(matchLabel & makeLabelRef)
	

#######################################################################
# Statements Flow

ctrlFlowAnno = 'CtrlFlow'

getCtrlFlow = annotation.Get(ctrlFlowAnno)
SetCtrlFlow = lambda flows: annotation.Set(ctrlFlowAnno, flows)


#######################################################################
# Flow Traversal

markStmtsFlow = base.Proxy()

stmtFlow = parse.Rule('''
	Assign(*) -> [next]
|	Label(*) -> [next]
|	Asm(*) -> [next]
|	If(_, true, false) -> [true{Cond("True")}, false{Cond("False")}]
|	While(_, stmt) -> [next{Cond("False")}, stmt{Cond("True")}]
|	NoStmt -> [next]
|	Continue(*) -> [cont]
|	Break(*) -> [brek]
|	Ret(*)-> [retn]
|	Branch(Sym(name)) -> [<lists.Lookup(!name,!lbls)>]
|	Branch(*) -> []
|	n(*) -> [next{Cond(n)}]
''')

stmtChildNext = parse.Rule('''
	While(_, _) -> <getStmtId>
|	_ -> next
''')


markStmtFlow \
	= SetCtrlFlow(
		combine.Try(traverse.All(combine.Try(getStmtId))) &
		stmtFlow
	)


markStmtFlow = ir.traverse.Stmt(
	stmts = markStmtsFlow,
	Wrapper = lambda x: markStmtFlow & scope.With(x, next=stmtChildNext)
)

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
		following = project.tail & (project.head & getStmtId | build._.next)
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

endOfModule = build._.NoStmt() & SetStmtId(build.Int(0)) & SetCtrlFlow(build.nil)
endOfModule = build.zero

if 0:
	markStmtFlow.subject = debug.Trace('markStmtFlow', markStmtFlow.subject)
	markStmtsFlow.subject = debug.Trace('markStmtsFlow', markStmtsFlow.subject)

markModuleFlow \
	= scope.With(
		ir.traverse.Module(stmts = markStmtsFlow),
		next=endOfModule, 
		cont=endOfModule, 
		brek=endOfModule, 
		retn=endOfModule,
		lbls=makeLableTable
	)

markFlow = markModuleFlow

MarkFlow = lambda: MarkStmtsIds() & markFlow


#######################################################################
# Graph Generation

makeNodeId = strings.ToStr()

makeAttr = lambda name, value: build._.Attr(name, value)

renderBox \
	= base.Adaptor(lambda term, context: term.factory.makeStr(box.stringify(term))) \
	| build.Str("???")

makeNodeLabel = parse.Rule('''
	If(cond,_,_)
		-> <<ir.pprint.expr>cond>
|	While(cond,_)
		-> <<ir.pprint.expr>cond>
|	_
		-> <ir.pprint.stmtKern>
|	n(*) 
		-> n
''') & renderBox

makeNodeShape = parse.Rule('''
	If(cond,_,_)
		-> "diamond"
|	While(cond,_)
		-> "diamond"
|	NoStmt
		-> "point"
|	_ 
		-> "box"
''')

makeNodeAttrs \
	= build.List([
		makeAttr("label", makeNodeLabel & box.escape),
		makeAttr("shape", makeNodeShape)
	])

makeEdgeLabel \
	= annotation.Get('Cond') \
	| build.Str("")

makeEdgeAttrs \
	= build.List([
		makeAttr("label", makeEdgeLabel & box.escape),
	])
	
makeNodeEdges \
	= getCtrlFlow \
	& traverse.Map(
		build._.Edge(
			makeNodeId,
			makeEdgeAttrs,
		)
	)

makeNode = build._.Node(
	getStmtId & makeNodeId, 
	makeNodeAttrs, 
	makeNodeEdges
)

makeNodes = lists.Concat(
	build.List([build.Term('Node("0", [Attr("shape", "point")], [])')]),
	unify.CollectAll(makeNode)
)

makeGraph = build._.Graph(makeNodes)


#######################################################################
# Graph Simplification

replaceStmtFlow = \
	combine.IfThenElse(
		getStmtId & match._.src,
		annotation.Del(stmtIdAnno) & annotation.Del(ctrlFlowAnno),
		annotation.Update(
			ctrlFlowAnno, 
			traverse.Map(
				combine.Try(match._.src & build._.dst)
			),
		)
	)

replaceStmtFlow = traverse.BottomUp(combine.Try(replaceStmtFlow))

matchNoStmts \
	= match.Appl("NoStmt", match.nil) \
	& combine.Where(getStmtId)\
	& combine.Where(getCtrlFlow)

collectNoStmts = unify.CollectAll(matchNoStmts)

getSingleFlow = getCtrlFlow & match.Pattern('[_]') & project.first


def removeNoStmts(term, context):
		noStmts = collectNoStmts.apply(term, context)
		print noStmts
		for noStmt in noStmts:
			new_context = transf.context.Context(context, ['src', 'dst'])
			new_context['src'] = getStmtId.apply(noStmt, context)
			new_context['dst'] = getSingleFlow.apply(noStmt, context)
			print new_context['src'], "INTO", new_context['dst']
			term = replaceStmtFlow.apply(term, new_context)
		return term

removeNoStmts = base.Adaptor(removeNoStmts)

simplifyFlow = removeNoStmts


#######################################################################
# Example


if __name__ == '__main__':
	import aterm.factory
	import sys
	factory = aterm.factory.Factory()
	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))

		#print ( pprint2.module  )(term)
		#print ( pprint2.module & renderBox )(term)

		term = MarkStmtsIds() (term)
		#print makeLableTable (term)
		#print (lists.Lookup(build.Str("main"), makeLableTable)) (term)
		#print term
		#term = (debug.Traceback(markFlow)) (term)
		term = markFlow (term)
		#print term
		#print
		
		print "*********"
		term = simplifyFlow (term)
		#print term
		print "*********"
		#sys.exit(0)
		
		#print makeNodes (term)
		#print makeEdges (term)
		
		term = makeGraph(term)
		print term
		print
		
		dotcode = lang.dot.stringify(term)
		print dotcode

		import gtk
		import ui.dotview
		win = ui.dotview.DotView()
		win.set_dotcode(dotcode)
		gtk.main()

