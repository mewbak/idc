'''Refactoring user input abstraction.'''


import gtk
import glade


# TODO: Generate dialog windows directly from term representation


class Inputter:
	
	def inputStr(self, title="", text=""):
		parent = None
		dialog = gtk.Dialog(
			title,
			parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
			gtk.STOCK_OK, gtk.RESPONSE_OK)
		)
		dialog.set_default_response(gtk.RESPONSE_OK)
		
  		textlabel = gtk.Label(text)
  		dialog.vbox.pack_start(textlabel)
  		
  		textentry = gtk.Entry()
  		textentry.set_activates_default(True)
  		dialog.vbox.add(textentry)

		dialog.show_all()
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			result = textentry.get_text()
		else:
			result = None
		
		dialog.destroy()
		return result
		

if __name__ == '__main__':
	import os
	os.chdir('..')
	inputter = Inputter()
	print inputter.inputStr("Title", "Question?")
