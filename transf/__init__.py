'''Term transformation framework. 

This framework allows to create complex term transformations from simple blocks.

It is inspired on the Stratego/XT framework. More information about it is
available at http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-0.16/manual/ .
'''


from transf import exception
from transf import base
from transf import scope

from transf import combinators
from transf import projection
from transf import matching
from transf import building
from transf import rewriters
from transf import traversal
from transf import unifiers

from transf import annotation

from transf import arith
from transf import lists
from transf import strings

from transf import debug

from transf import grammar

import transf._factory as _factory
factory = _factory.Factory()



