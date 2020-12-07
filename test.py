
from cc import *
import ply.lex as lex
import ply.yacc as yacc

l = lex.lex()
y = yacc.yacc()

import sys

class Writer:
    def __init__(self, hfile, srcfile):
        self.header_file = hfile
        self.source_file = srcfile
        self.header_indent = 0
        self.source_indent = 0
        self.variables = []
        self.is_template_context = False

    def ast(self, ast, filename):
        self.current_file = filename
        for e in ast:
            e.cg(self)

    def header(self, *parts):
        self.header_file.write('\t'*self.source_indent + ''.join(parts) + '\n')

    def header_block(self, *parts):
        self.header(*parts or '{')
        self.header_indent += 1

    def header_leave(self, *parts):
        self.header_indent -= 1
        self.header(*parts or '}')

    def source(self, *parts):
        self.source_file.write('\t'*self.source_indent + ''.join(parts) + '\n')

    def source_block(self, *parts):
        self.source(*parts or '{')
        self.source_indent += 1

    def source_leave(self, *parts):
        self.source_indent -= 1
        self.source(*parts or '}')

    def variable(self, v):
        if '::' in v:
            return v # b/c it is scoped, therefore neither local nor in content
        name = re.search(r'(\w+)', v).group(1)
        if name in self.variables:
            return v
        m = re.search(r'([^\w]*)(.*)', v)
        return m.group(1) + 'content.' + m.group(2)

with open(sys.argv[1], 'r') as f, open('header.h', 'w') as h:
    ast = y.parse(f.read())
    cg = Writer(h, sys.stdout)
    import os
    cg.ast(ast, os.path.realpath(sys.argv[1]))

