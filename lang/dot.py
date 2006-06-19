'''Dot language support.

See U{http://www.graphviz.org/}.
'''

import aterm
import transf
import box


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

ppNodes = transf.traverse.Map(ppNode)

ppNodeEdge = transf.parse.Rule('''
		Edge(dst, attrs) 
			-> H([ <<id> src>, "->", <<id> dst>, <<ppAttrs> attrs> ])
''')

ppNodeEdges = transf.parse.Rule('''
		Node(src, _, edges) 
			-> <<Map(ppNodeEdge)> edges>
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


import walker


class Writer(walker.Walker):
	'''Writes boxes trhough a formatter.'''

	def __init__(self, fp):
		walker.Walker.__init__(self)
		self.fp = fp
	
	def write(self, dot):
		self.writeGraph(*dot.args)
	
	def writeGraph(self, nodes):
		self.fp.write("digraph {\n")
		for node in nodes:
			self.writeNode(*node.args)
		for node in nodes:
			self.writeNodeEdges(*node.args)
		self.fp.write("}")
		
	def writeNode(self, id, attrs, edges):
		self.writeId(id)
		self.writeAttrs(attrs)
		self.fp.write('\n')

	def writeNodeEdges(self, src, attrs, edges):
		for edge in edges:
			self.writeEdge(src, *edge.args)

	def writeEdge(self, src, dst, attrs):
		self.writeId(src)
		self.fp.write('->')
		self.writeId(dst)
		self.writeAttrs(attrs)
		self.fp.write('\n')

	def writeAttrs(self, attrs):
		self.fp.write('[')
		sep = ''
		for attr in attrs:
			self.fp.write(sep)
			self.writeAttr(*attr.args)
			sep = ','
		self.fp.write(']')
		
	def writeAttr(self, name, value):
		self.writeId(name)
		self.fp.write('=')
		self.writeId(value)
	
	def writeId(self, id):
		self.fp.write(str(id.value))
		

def write(dot, fp):
	writer = Writer(fp)
	writer.write(dot)
	

def stringify(dot):
	try:
		from cStringIO import StringIO
	except ImportError:
		from StringIO import StringIO
	fp = StringIO()
	write(dot, fp)
	return fp.getvalue()	