'''Term transformation framework. 

This framework allows to create complex term transformations from simple blocks.
It is inspired on the U{Stratego/XT<http://www.stratego-
language.org/Stratego/StrategoXT>}, adapted to Python idiosyncracies.

The basic block is a L{transformation<base.Transformation>} -- an object which
attemtps to transform a L{aterm.term.Term} within a specified
L{context<context.Context>} and returns the transformed term on success or
raises an L{exception<exception.Failure>} on failure. A
L{contex<context.Context>} is a mutable dictionary-like object, which holds
named term variables.

Another implicit concept is a transformation factory -- any callable which takes
a combination of terms, transformations, and other transformations factories and
returns a transformation. Due to Python's dynamic typing there is no need for
transformation factories to derive a particular class. Therefore any
transformation class or transformation yielding functions can be used.

To help distinguish between transformations and transformation factories,
throughout the code, transformations instances' names start with a lower-case
letter, while transformations factories start with a capital.

More information about Stratego/XT can be found in its 
U{Manual <http://www.stratego-language.org/Stratego/StrategoDocumentation>} and its
U{API Documentation <http://nix.cs.uu.nl/dist/stratego/stratego-lib-docs-0.16/docs/>}.
'''

__docformat__ = 'epytext'


from transf import exception
from transf import base
from transf import util
from transf import variable
from transf import scope

from transf import combine
from transf import project
from transf import match
from transf import build
from transf import congruent

from transf import lists
from transf import traverse
from transf import unify

from transf import arith
from transf import strings
from transf import table

from transf import annotation
from transf import path

from transf import debug

from transf import parse




