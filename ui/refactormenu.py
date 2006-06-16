'''Refactoring and view menus.'''

import gtk

import refactoring

from ui import inputter


class RefactorMenu(gtk.Menu):
	
	refactoring_factory = refactoring.Factory()
	
	def __init__(self, model):
		gtk.Menu.__init__(self)
		self.model = model
		
		for refactoring in self.refactoring_factory.refactorings.itervalues():
			menuitem = gtk.MenuItem(refactoring.name())
			menuitem.connect("realize", self.on_menuitem_realize, refactoring)
			menuitem.connect("activate", self.on_menuitem_activate, refactoring)
			menuitem.show()
			self.append(menuitem)

	def on_menuitem_realize(self, menuitem, refactoring):
		term = self.model.term.get()
		selection = self.model.selection.get()
		if refactoring.applicable(term, selection):
			menuitem.set_state(gtk.STATE_NORMAL)
		else:
			menuitem.set_state(gtk.STATE_INSENSITIVE)
	
	def on_menuitem_activate(self, menuitem, refactoring):
		print refactoring.name()
		
		# Ask user input
		args = refactoring.input(
			self.model.term.get(), 
			self.model.selection.get(),
			inputter.Inputter()
		)
		
		self.model.apply_refactoring(refactoring, args)

