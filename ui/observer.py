"""Implementation of the observer pattern as described by Gamma et. al.
See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/131499 .
"""

class Subject:
	"""Abstract subject class."""
	
	def __init__(self):
		self._observers = []

	def attach(self, observer):
		"""Attach an observer to this subject."""
		if not observer in self._observers:
			self._observers.append(observer)

	def detach(self, observer):
		"""Detach an observer from this subject."""
		try:
			self._observers.remove(observer)
		except ValueError:
			pass

	def notify(self, modifier = None):
		"""Notifies an update. The modifier argument can be used if you don't 
		want an observer which has modified the subject to be updated again.
		"""
		for observer in self._observers:
			if modifier != observer:
				observer(self)

class Observer:
	"""Interface for observers. It is not imperative for observers to derive 
	from this class, provided the interface is implemented.
	"""
	
	def __call__(self, subject):
		raise NotImplementedError