'''Dot pretty-printing.'''


import aterm
import transf

from lang import box


ppId = transf.strings.tostr

ppAttr = transf.parse.Rule('''
		Attr(name, value) 
			-> H([ <<id> name>, "=", <<id> value> ])
''')

ppAttrs = transf.parse.Transf('''
		!H([ "[", <Map(ppAttr); box.commas>, "]" ])
''')

ppNode = transf.parse.Rule('''
		Node(nid, attrs, _)
			-> H([ <<id> nid>, <<ppAttrs> attrs> ])
''')

ppNodes = transf.lists.Map(ppNode)

ppNodeEdge = transf.parse.Rule('''
		Edge(dst, attrs) 
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
''')

ppNodeEdges = transf.parse.Rule('''
		Node(src, _, edges) 
			-> <<Map(ppNodeEdge)> edges>
''')

ppEdges = transf.lists.Map(ppNodeEdges) * transf.lists.concat

ppGraph = transf.parse.Rule(r'''
		Graph(nodes)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( <<ppNodes> nodes> ),
				V( <<ppEdges> nodes> ),
				H([ "}" ])
			])
''')

pprint = ppGraph
