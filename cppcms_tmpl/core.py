
from .common import non_empty_sequence

class CppDecl:
    'cpp_decl : BEGIN_STATEMENT CPP COMMAND END_STATEMENT'
    def __init__(self, p):
        p[0] = self
        self.cpp_command = p[3]
        self.lineno = p.lineno(3)
    def __repr__(self):
        return 'CppDecl(' + self.cpp_command + ')@' + str(self.lineno)
    def cg(self, w):
        if w.is_template_context:
            w.source('#line %d "%s"' % (self.lineno, w.current_file))
            w.source(self.cpp_command)
        else:
            w.header('#line %d "%s"' % (self.lineno, w.current_file))
            w.header(self.cpp_command)

class EndBlock:
    'end_block : BEGIN_STATEMENT END optional_block_type END_STATEMENT'
    def __init__(self, p):
        p[0] = self
        self.type = p[3]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'EndBlock(' + (self.type if self.type else 'any') + ')@' + str(self.lineno)

p_translation_unit = lambda p: non_empty_sequence(p)
p_translation_unit.__doc__ =  '''translation_unit : translation_unit decl
                                                  | decl'''

def p_decl(p):
    '''decl : cpp_decl
            | skin_decl'''
    p[0] = p[1]

def p_optional_block_type(p):
    '''optional_block_type : TMPL
                           | VIEW
                           | SKIN
                           | ITEM
                           |'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ''

