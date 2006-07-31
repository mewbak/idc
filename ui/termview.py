"""Aterm inspector view."""


import gtk
import gobject

from ui import view

import aterm.types


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
		if not self.tail:
			return None
		else:
			return TermTreeIter(
				self.path[:-1] + (self.path[-1] + 1,), 
				self.parents,
				self.tail.head,
				self.tail.tail
			)
	
	def _children(self):
		term = self.head
		type = term.type
		if type & aterm.types.LIST:
			return term
		elif type == aterm.types.APPL:
			return term.factory.makeList(term.args)
		else:
			return term.factory.makeNil()
		
	def children(self):
		children = self._children()
		if not children:
			return None
		else:
			return TermTreeIter(
				self.path + (0,),
				self.parents + ((self.head, self.tail),),
				children.head,
				children.tail
			)

	def has_child(self):
		children = self._children()
		return bool(children)
		
	def n_children(self):
		children = self._children()
		return len(children)
	
	def nth_child(self, n):
		children = self._children()
		if n > len(children):
			return None
		else:
			for i in range(n):
				children = children.tail
			return TermTreeIter(
				self.path + (n,),
				self.parents + ((self.head, self.tail),),
				children.head,
				children.tail
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
		type = term.type

		if column == 0:			
			if type == aterm.types.INT:
				return str(term.value)
			elif type == aterm.types.REAL:
				return str(term.value)
			elif type == aterm.types.STR:
				return repr(term.value)
			elif type == aterm.types.NIL:
				return '[]'
			elif type == aterm.types.CONS:
				return '[...]'
			elif type == aterm.types.APPL:
				return term.name
			else:
				return '?'
		elif column == 1:
			if type == aterm.types.INT:
				return 'INT'
			elif type == aterm.types.REAL:
				return 'REAL'
			elif type == aterm.types.STR:
				return 'STR'
			elif type & aterm.types.LIST:
				return 'LIST'
			elif type == aterm.types.APPL:
				return 'APPL'
			else:
				return '?'
		elif column == 2:
			if term.annotations:
				return ', '.join([str(anno) for anno in term.annotations])
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


class TermWindow(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self)

		self.set_title('Term Inspector')
		self.set_default_size(320, 480)

		scrolled_window = gtk.ScrolledWindow()
		self.add(scrolled_window)
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		
		self.treeview = treeview = gtk.TreeView()
		scrolled_window.add(self.treeview)
		treeview.set_enable_search(False)
		
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Term", renderer, text=0)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Type", renderer, text=1)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Annotations", renderer, text=2)
		treeview.append_column(column)

		self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

		self.show_all()

	def set_term(self, term):
		treeview = self.treeview
		treemodel = TermTreeModel(term)
		treeview.set_model(treemodel)
		treeview.expand_all()

	def get_path(self, path):
		if path is not None:
			path = [int(i) for i in path]
			path.reverse()
			path = tuple([0] + path)
			return path
		else:
			return None

		

class TermView(TermWindow, view.View):
	
	def __init__(self, model):
		TermWindow.__init__(self)
		view.View.__init__(self, model)
		
		model.connect('notify::term', self.on_term_update)
		model.connect('notify::selection', self.on_selection_update)
			
		self.connect('destroy', self.on_window_destroy)
		
		if model.get_term() is not None:
			self.on_term_update(model.term)
		if model.get_selection() is not None:
			self.on_selection_update(model.selection)

	def get_name(self, name):
		return 'Inspector View'
		
	def on_term_update(self, term):
		self.set_term(term)

	def on_selection_update(self, selection):
		start, end = selection
		
		start = self.get_path(start)
		end = self.get_path(end)
		
		if start is not None and end is not None:
			tree_selection = self.treeview.get_selection()
			tree_selection.unselect_all()
			tree_selection.select_range(start, end)
			self.treeview.scroll_to_cell(start)
			#self.treeview.set_cursor(start)
	
	def on_window_destroy(self, event):
		model = self.model
		model.disconnect('notify::term', self.on_term_update)
		model.disconnect('notify::selection', self.on_selection_update)
		

class TermViewFactory(view.ViewFactory):
	
	def get_name(self):
		return 'Term'
	
	def can_create(self, model):
		return True
	
	def create(self, model):
		return TermView(model)
	

if __name__ == '__main__':
	view.main(TermView)

