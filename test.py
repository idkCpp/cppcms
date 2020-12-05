
from cc import *
import ply.lex as lex
import ply.yacc as yacc

l = lex.lex()
y = yacc.yacc()

import sys

with open(sys.argv[1], 'r') as f:
    if False:
        l.input(f.read())

        while True:
            tok = l.token()
            if not tok:
                break
            print(tok)
    else:
        print(y.parse(f.read()))
