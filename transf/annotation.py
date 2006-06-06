'''Annotation transformations.'''


from transf import exception
from transf import base


class Set(base.Transformation):
	
	def __init__(self, label, value):
		base.Transformation.__init__(self)
		self.label = label
		self.value = value
		
	def apply(self, term, context):
		label = self.label.apply(term, context)
		print label
		label = term.factory.makeAppl(
			label, 
			term.factory.makeList([term.factory.makeWildcard()])
		)
		print label
		value = self.value.apply(term, context)
		print value
		value = label.make(value)
		print value
		print
		return term.setAnnotation(label, value)
		

class Get(base.Transformation):
	
	def __init__(self, label):
		base.Transformation.__init__(self)
		self.label = label
		
	def apply(self, term, context):
		print term
		label = self.label.apply(term, context)
		print label
		label = term.factory.makeAppl(
			label, 
			term.factory.makeList([term.factory.makeWildcard()])
		)
		print label
		try:
			value = term.getAnnotation(label)
			value = value.args.head
			print value
			print
			return value
		except ValueError:
			raise exception.Failure
		


