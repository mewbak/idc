'''Dot pretty-printing.'''


import aterm
from transf import lib
from lang import box


ppId = lib.strings.tostr

ppAttr = lib.parse.Rule('''
		Attr(name, value)
			-> H([ <<id> name>, "=", <<id> value> ])
''')

ppAttrs = lib.parse.Transf('''
		!H([ "[", <Map(ppAttr); box.commas>, "]" ])
''')

ppNode = lib.parse.Rule('''
		Node(nid, attrs, _)
			-> H([ <<id> nid>, <<ppAttrs> attrs> ])
''')

ppNodes = lib.lists.Map(ppNode)

ppNodeEdge = lib.parse.Rule('''
		Edge(dst, attrs)
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
''')

ppNodeEdges = lib.parse.Rule('''
		Node(src, _, edges)
			-> <<Map(ppNodeEdge)> edges>
''')

ppEdges = lib.lists.Map(ppNodeEdges) * lib.lists.concat

ppGraph = lib.parse.Rule(r'''
		Graph(nodes)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( <<ppNodes> nodes> ),
				V( <<ppEdges> nodes> ),
				H([ "}" ])
			])
''')

pprint = ppGraph
