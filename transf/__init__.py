'''Term transformation framework. 

This framework allows to create complex term transformations from simple blocks.

It is inspired on the Stratego/XT framework. More information about it is
available at http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/ .
'''


import os
import os.path
import types

# automatically populate the package namespace from the modules
__all__ = []
for _dir in __path__:
	for _modnam in os.listdir(_dir):
		if _modnam.endswith('.py') and not _modnam.startswith('_'):
			_modnam = _modnam[:-3]
			_mod = getattr(__import__(__name__ + '.' + _modnam), _modnam)
			__all__.append(_modnam)
			for _objnam, _obj in _mod.__dict__.iteritems():
				if not _objnam.startswith('_') and not isinstance(_obj, types.ModuleType):
					globals()[_objnam] = _obj
					__all__.append(_objnam)
				del _objnam, _obj
			del _mod
	del _modnam
del _dir


from transf._factory import Factory as _Factory
factory = _Factory()
del _Factory
