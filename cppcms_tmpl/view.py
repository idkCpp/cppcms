
from .common import sequence

class ViewDecl:
    'view_decl : begin_view_block template_seq end_block'
    def __init__(self, p):
        p[0] = self
        self.begin = p[1]
        self.seq = p[2]
        self.end = p[3]
    def __repr__(self):
        return 'ViewDecl(' + repr(self.begin) + ';' + repr(self.seq) + ';' + repr(self.end) + ')'
    def register(module):
        module['p_template_seq'] = lambda p: sequence(p)
        module['p_template_seq'].__doc__ = '''template_seq : template_seq template_decl
                                                           | template_decl
                                                           |'''
    def cg(self, w):
        self.begin.cg(w)

        for e in self.seq:
            e.cg(w, self.begin.identifier)

        w.header('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.header_leave()
        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave()

class BeginViewBlock:
    '''begin_view_block : BEGIN_STATEMENT VIEW IDENTIFIER USES possibly_scoped_identifier END_STATEMENT
                        | BEGIN_STATEMENT VIEW IDENTIFIER USES possibly_scoped_identifier EXTENDS IDENTIFIER END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.identifier = p[3]
        self.contenttype = p[5]
        if len(p) == 7:
            self.extends = None
        else:
            self.extends = p[7]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'BeginViewBlock("' + self.identifier + '";' + self.contenttype + (';' + self.extends if self.extends else '') + ')@' + str(self.lineno)
    def cg(self, w):
        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header('struct ', self.identifier, ' : public ', self.extends if self.extends else 'cppcms::base_view')

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header_block()

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header(self.contenttype, ' &content;')

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header(self.identifier, '(std::ostream &_s, ', self.contenttype, ' &_content) : ', ( self.extends + '(_s,_content),' ) if self.extends else '', 'content(_content),_domain_id(0)')

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header_block()

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header('_domain_id=booster::locale::ios_info::get(_s).domain_id();')

        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header_leave()

