'''Term types constants.'''


INT  = 0x01
REAL = 0x02
STR  = 0x04
NIL  = 0x08
CONS = 0x10
APPL = 0x20

LIT  = INT | REAL | STR

LIST = NIL | CONS
