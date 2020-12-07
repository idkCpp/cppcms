
from .common import non_empty_sequence

class SkinDecl:
    'skin_decl : begin_skin_block view_seq end_block'
    def __init__(self, p):
        p[0] = self
        self.begin = p[1]
        self.seq = p[2]
        self.end = p[3]
    def __repr__(self):
        return 'SkinDecl(' + repr(self.begin) + ';' + repr(self.seq) + ';' + repr(self.end) + ')'
    def register(module):
        module['p_view_seq'] = lambda p: non_empty_sequence(p)
        module['p_view_seq'].__doc__ = '''view_seq : view_seq view_decl
                                                   | view_decl'''
    def cg(self, w):
        self.begin.cg(w)

        for e in self.seq:
            e.cg(w)

        w.header('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.header_leave('} // end of namespace ', self.begin.name)
        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave('} // end of namespace ', self.begin.name)

class BeginSkinBlock:
    'begin_skin_block : BEGIN_STATEMENT SKIN IDENTIFIER END_STATEMENT'
    def __init__(self, p):
        p[0] = self
        self.name = p[3]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'BeginSkinBlock("' + self.name + '")@' + str(self.lineno)
#    def register(module):
#        module['block_types'].append('SKIN')
    def cg(self, w):
        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header_block('namespace ', self.name, ' {')
        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source_block('namespace ', self.name, ' {')

