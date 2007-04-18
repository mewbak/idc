'''Dot pretty-printing.'''


import aterm
from transf import lib
from lang import box


lib.parse.Transfs('''

ppId = lib.strings.tostr

ppAttr = {
		Attr(name, value)
			-> H([ <<id> name>, "=", <<id> value> ])
}

ppAttrs = {
		!H([ "[", <Map(ppAttr); box.commas>, "]" ])
}

ppNode = {
		Node(nid, attrs, _)
			-> H([ <<id> nid>, <<ppAttrs> attrs> ])
}

ppNodes = lib.lists.Map(ppNode)

ppNodeEdge = [
		Edge(dst, attrs)
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
}

ppNodeEdges = {
		Node(src, _, edges)
			-> <<Map(ppNodeEdge)> edges>
}

ppEdges =
	lib.lists.Map(ppNodeEdges) ;
	lib.lists.concat

ppGraph = {
		Graph(nodes)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( <<ppNodes> nodes> ),
				V( <<ppEdges> nodes> ),
				H([ "}" ])
			])
}

pprint = ppGraph

''')
