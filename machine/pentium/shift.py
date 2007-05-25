'''Shift and rotate instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


#AsmSAx(size, dir, dst, src) =
#	with
#		type = Word(size),
#		tmp = temp
#	in
#		![
#			Assign(type, tmp, src), Binary(dir(type),dst, src)
#			Assign(type, tmp, Binary(And(type), dst, src)),
#			*<LogFlags(size, !tmp)>
#		]
#	end
#	[Assign(
#	[dst,src] -> [
#		Assign(<Word(size)>, dst, Binary(<op>,dst,src)),
#		*<LogFlags(size, !dst)>
#	]



''')


