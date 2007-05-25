''' arithmetic instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


asmCLTD =
	[] -> [Assign(Bool,<df>,Lit(Bool,0))]


''')
