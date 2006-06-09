'''Dot language support.

See U{http://www.graphviz.org/}.
'''

import aterm
import transf
import box


ppId = transf.strings.ToStr

ppAttr = transf.parse.Rule('''
		Attr(name, value) 
			-> H([ <<id> name>, "=", <<id> value> ])
''')

ppAttrs = transf.parse.Transf('''
		!H([ "[", <map(ppAttr); box.commas>, "]" ])
''')

ppNode = transf.parse.Rule('''
		Node(nid, attrs, _)
			-> H([ <<id> nid>, <<ppAttrs> attrs> ])
''')

ppNodes = transf.traverse.Map(ppNode)

ppNodeEdge = transf.parse.Rule('''
		Edge(dst, attrs) 
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
''')

ppNodeEdges = transf.parse.Rule('''
		Node(src, _, edges) 
			-> <<map(ppNodeEdge)> edges>
''')

ppEdges = transf.traverse.Map(ppNodeEdges) & transf.lists.concat

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


