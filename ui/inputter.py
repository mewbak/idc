'''Refactoring user input abstraction.'''


import gtk
import glade


# TODO: Generate dialog windows directly from term representation


class TextDialog(glade.GladeWindow):
	
	def __init__(self):
		glade.GladeWindow.__init__(self, "inputter.glade", "textdialog")
	
	def aon_okbutton_clicked(self, *args):
		print "OK!"
		self.widget.destroy()
		
	def aon_cancelbutton_clicked(self, *args):
		print "Cancel!"
		self.widget.destroy()


class Inputter:
	
	def inputStr(self, title="", text=""):
		dialog = TextDialog()
		dialog.textlabel.set_text(text)
		response = dialog.widget.run()

		if response == gtk.RESPONSE_OK:
			result = dialog.textentry.get_text()
		else:
			result = None
		
		dialog.widget.destroy()
		return result
		

if __name__ == '__main__':
	import os
	os.chdir('..')
	inputter = Inputter()
	print inputter.inputStr("", "Question?")
