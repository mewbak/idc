'''Term transformation framework. 

This framework allows to create complex term transformations from simple blocks.

It is inspired on the Stratego/XT framework. More information about it is
available at http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/ .
'''


from transf.exception import *
from transf.base import *
from transf.combinators import *
from transf.projection import *
from transf.matching import *
from transf.building import *
from transf.rewriters import *
from transf.traversal import *
from transf.unifiers import *
from transf.arith import *

import transf._factory as _factory
factory = _factory.Factory()



