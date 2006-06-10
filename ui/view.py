'''View support.
'''


class View:
	
	def __init__(self, model):
		self.model = model
	
	def get_name(self):
		raise NotImplementedError
	
	def destroy(self):
		raise NotImplementedError


class ViewFactory:
	"""Base class for model views."""

	def __init__(self):
		pass
	
	def get_name(self):
		raise NotImplementedError

	def is_applicable(self, model):
		raise NotImplementedError

	def create(self, model):
		raise NotImplementedError


# TODO: write a simple main to test views