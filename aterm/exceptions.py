'''Exception class hierarchy.'''


class BaseException(Exception):
	'''Base class for all term-related exceptions.'''
	pass


class ParseException(BaseException):
	'''Error parsing textual representation of terms.'''
	pass

	
class EmptyListException(BaseException):
	'''Attempt to access beyond the end of the list.'''
	pass

