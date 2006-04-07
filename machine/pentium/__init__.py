'''Intel 32-bit architecture processors.'''


from machine import Machine


class Pentium(Machine):
	'''Intel 32-bit architecture processors.'''

	def load(self, factory, fp):
		from machine.pentium.att_lexer import Lexer
		from machine.pentium.att_parser import Parser
		
		lexer = Lexer(fp)
		parser = Parser(lexer, factory = factory)
		term = parser.start()
		return term			

	def translate(self, term):
		from machine.pentium.translator import Translator
		
		walker = Translator(term.factory)
		term = walker.module(term)				
		return term

