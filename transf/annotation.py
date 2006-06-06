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
		label = term.factory.makeAppl(
			label, 
			term.factory.makeList([term.factory.makeWildcard()])
		)
		value = self.value.apply(term, context)
		value = label.make(value)
		return term.setAnnotation(label, value)
		

class Get(base.Transformation):
	
	def __init__(self, label):
		base.Transformation.__init__(self)
		self.label = label
		
	def apply(self, term, context):
		label = self.label.apply(term, context)
		label = term.factory.makeAppl(
			label, 
			term.factory.makeList([term.factory.makeWildcard()])
		)
		try:
			value = term.getAnnotation(label)
			value = value.args.head
			return value
		except ValueError:
			raise exception.Failure
		


