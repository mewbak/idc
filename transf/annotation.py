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
		value = self.value.apply(term, context)
		return term.setAnnotation(label, value)
		

class Get(base.Transformation):
	
	def __init__(self, label):
		base.Transformation.__init__(self)
		self.label = label
		
	def apply(self, term, context):
		label = self.label.apply(term, context)
		try:
			return term.getAnnotation(label)
		except ValueError:
			raise exception.Failure
		


