'''Dot pretty-printing.'''


from transf import parse
from lang import box


parse.Transfs('''

ppId = strings.tostr

ppAttr = {
		Attr(name, value)
			-> H([ <<id> name>, "=", <<id> value> ])
}

ppAttrs =
		!H([ "[", <Map(ppAttr); box.commas>, "]" ])

ppNode = {
		Node(nid, attrs, _)
			-> H([ <<id> nid>, <<ppAttrs> attrs> ])
}

ppNodes = lists.Map(ppNode)

ppNodeEdge = {
		Edge(dst, attrs)
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
}

ppNodeEdges = {
		Node(src, _, edges)
			-> <<Map(ppNodeEdge)> edges>
}

ppEdges =
	lists.Map(ppNodeEdges) ;
	lists.concat

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
