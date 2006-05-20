"""Aterm inspector window."""


import gtk
import gobject

from ui import glade

import aterm


class TermTreeIter:
	"""Iterator for TermTreeModel."""

	def __init__(self, path, parents, head, tail):
		self.path = path
		self.parents = parents
		self.head = head
		self.tail = tail
	
	def term(self):
		return self.head
	
	def next(self):
		if self.tail.isEmpty():
			return None
		else:
			return TermTreeIter(
				self.path[:-1] + (self.path[-1] + 1,), 
				self.parents,
				self.tail.getHead(),
				self.tail.getTail()
			)
	
	def _children(self):
		term = self.head
		type = term.getType()
		if type == aterm.LIST:
			return term
		elif type == aterm.APPL:
			return term.getArgs()
		else:
			return term.factory.makeNil()
		
	def children(self):
		children = self._children()
		if children.isEmpty():
			return None
		else:
			return TermTreeIter(
				self.path + (0,),
				self.parents + ((self.head, self.tail),),
				children.getHead(),
				children.getTail()
			)

	def has_child(self):
		children = self._children()
		return not children.isEmpty()
		
	def n_children(self):
		children = self._children()
		return children.getLength()
	
	def nth_child(self, n):
		children = self._children()
		if n > children.getLength():
			return None
		else:
			for i in range(n):
				children = children.getTail()
			return TermTreeIter(
				self.path + (n,),
				self.parents + ((self.head, self.tail),),
				children.getHead(),
				children.getTail()
			)	
	
	def parent(self):
		if not len(self.parents):
			return None
		else:
			return TermTreeIter(
				self.path[:-1],
				self.parents[:-1],
				self.parents[-1][0],
				self.parents[-1][1],			
			)


class TermTreeModel(gtk.GenericTreeModel):
	''''Generic tree model for an aterm.'''

	def __init__(self, term):
		'''constructor for the model.  Make sure you call
		PyTreeModel.__init__'''
		gtk.GenericTreeModel.__init__(self)
		
		self.top = TermTreeIter((), (), term, term.factory.makeNil())

	# the implementations for TreeModel methods are prefixed with on_
	
	def on_get_flags(self):
		'''returns the GtkTreeModelFlags for this particular type of model'''
		return 0 # gtk.TREE_MODEL_ITERS_PERSIST
	   
	def on_get_n_columns(self):
		'''returns the number of columns in the model'''
		return 3
	   
	def on_get_column_type(self, index):
		'''returns the type of a column in the model'''
		return gobject.TYPE_STRING
	   
	def on_get_path(self, node):
		'''returns the tree path(a tuple of indices at the various
		levels) for a particular node.'''
		return node.path
	   
	def on_get_iter(self, path):
		'''returns the node corresponding to the given path.  In our
		case, the node is the path'''
		assert path[0] == 0
		node = self.top
		for n in path[1:]:
			node = node.nth_child(n)
		return node
	   
	def on_get_value(self, node, column):
		'''returns the value stored in a particular column for the node'''
		
		term = node.term()
		type = term.getType()

		if column == 0:			
			if type == aterm.INT:
				return str(term.getValue())
			elif type == aterm.REAL:
				return str(term.getValue())
			elif type == aterm.STR:
				return repr(term.getValue())
			elif type == aterm.LIST:
				return '[...]'
			elif type == aterm.APPL:
				return term.getName().getValue()
			elif type == aterm.WILDCARD:
				return '_'
			elif type == aterm.VAR:
				return term.getName()
			else:
				return '?'
		elif column == 1:
			if type == aterm.INT:
				return 'INT'
			elif type == aterm.REAL:
				return 'REAL'
			elif type == aterm.STR:
				return 'STR'
			elif type == aterm.LIST:
				return 'LIST'
			elif type == aterm.APPL:
				return 'APPL'
			elif type == aterm.WILDCARD:
				return 'WILDCARD'
			else:
				return 'VAR'
		elif column == 2:
			value = ''
			sep = ''
			annos = term.getAnnotations()
			while not annos.isEmpty():
				label = annos.getHead()
				annos = annos.getTail()
				anno = annos.getHead()
				annos = annos.getTail()
				value += sep + str(label) + ':' + str(anno)
				sep = ','
			return value
		else:
			return None
	   
	def on_iter_next(self, node):
		'''returns the next node at this level of the tree'''
		return node.next()
		
	def on_iter_children(self, node):
		'''returns the first child of this node'''
		return node.children()
		
	def on_iter_has_child(self, node):
		'''returns true if this node has children'''
		return node.has_child()
		
	def on_iter_n_children(self, node):
		'''returns the number of children of this node'''
		if node is None:
			return 1
		else:
			return node.n_children()
		   
	def on_iter_nth_child(self, node, n):
		'''returns the nth child of this node'''
		if node is None:
			assert n == 0
			return self.top
		else:
			return node.nth_child(n)
		
	def on_iter_parent(self, node):
		'''returns the parent of this node'''
		return node.parent()


class InspectorWindow(glade.GladeWindow):

	def __init__(self, main_window):
		glade.GladeWindow.__init__(self, "./ui/inspector.glade", "inspector_window")

		self.main_window = main_window
		
		treeview = self.treeview

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Term", renderer, text=0)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Type", renderer, text=1)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Annotations", renderer, text=2)
		treeview.append_column(column)

		document = self.main_window.document
		document.term.attach(self.on_term_update)
		document.selection.attach(self.on_selection_update)
		
		if document.term.get() is not None:
			self.on_term_update(document.term)
		if document.selection.get() is not None:
			self.on_selection_update(document.selection)
		
	def on_term_update(self, term):
		term = term.get()
		treeview = self.treeview
		model = TermTreeModel(term)
		treeview.set_model(model)
		treeview.expand_all()

	def on_selection_update(self, selection):
		start, end = selection.get()
		path = start
		
		if path is not None:
			path = [i.getValue() for i in path]
			path.reverse()
			path = tuple([0] + path)
		
			print path 
			
			#self.treeview.get_selection().select_path(path)
			self.treeview.scroll_to_cell(path)
			self.treeview.set_cursor(path)
	
	def on_inspector_window_destroy(self, event):
		document = self.main_window.document

		document.term.detach(self.on_term_update)
		document.selection.detach(self.on_selection_update)
		self.main_window.inspector.set_active(False)
		self.main_window.inspector_window = None

		# TODO: deactivate
		
	
