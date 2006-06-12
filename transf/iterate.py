'''Transformations for iterating terms.'''


def Repeat(operand):
	'''Applies a transformation until it fails.'''
	repeat = base.Proxy()
	repeat.subject = Try(operand & repeat)
	return repeat


