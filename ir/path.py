'''Path annotation.'''


from transf import *
from ir.common import *


# Only annotate term applications
annotate = path.Annotate(match.anAppl)