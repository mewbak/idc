'''Term types constants.'''


INT = 0x01
REAL = 0x02
STR = 0x04

LIT = INT | REAL | STR

NIL = 0x08
CONS = 0x10

LIST = NIL | CONS

APPL = 0x20

