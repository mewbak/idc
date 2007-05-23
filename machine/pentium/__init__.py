'''Intel 32-bit architecture processors.'''


from machine import Machine


class Pentium(Machine):
	'''Intel 32-bit architecture processors.'''

	def load(self, factory, fp):
		from lang.asm.att_lexer import Lexer
		from lang.asm.att_parser import Parser

		lexer = Lexer(fp)
		parser = Parser(lexer, factory = factory)
		term = parser.start()
		return term

	def translate(self, term):
		from machine.pentium import translator
		from transf.context import Context

		term = translator.module.apply(term, Context())
		return term

