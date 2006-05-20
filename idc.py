#!/usr/bin/env python

import sys

from ui.main import MainApp

if __name__ == '__main__':
	app = MainApp()
	if len(sys.argv) > 1:
		app.document.open_asm(sys.argv[1])
	app.main()


