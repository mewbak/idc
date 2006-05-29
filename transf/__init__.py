'''Term transformation framework. 

This framework allows to create complex term transformations from simple blocks.

It is inspired on the Stratego/XT framework. More information about it is
available at http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/ .
'''

from transf.base import *
from transf.term import *
from transf.combinators import *
from transf.traversers import *
from transf.rewriters import *

from transf._factory import Factory as _Factory
factory = _Factory()