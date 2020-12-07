
class TemplateDecl:
    '''template_decl : begin_template_block html_block end_block
                     | abstract_template_decl'''
    def __init__(self, p):
        p[0] = self
        if len(p) == 4:
            self.is_abstract = False
            self.begin = p[1]
            self.seq = p[2]
            self.end = p[3]
        else:
            self.is_abstract = True
            self.begin = p[1]
    def __repr__(self):
        r = 'TemplateDecl(' + repr(self.begin)
        if self.is_abstract:
            r += ';abstract)'
        else:
            r += ';' + repr(self.seq) + ';' + repr(self.end)
        r += ')'
        return r
    def cg(self, w, view):
        self.begin.cg(w, view)

        if not self.is_abstract:
            w.is_template_context = True
            for e in self.seq:
                e.cg(w)
            w.is_template_context = False

            w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
            w.source_leave('} // end of template ', self.begin.identifier)

class BeginTemplateBlock:
    '''begin_template_block : BEGIN_STATEMENT TMPL IDENTIFIER LPAREN expr_list RPAREN END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.identifier = p[3]
        self.params = p[5]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'BeginTemplateBlock(' + self.identifier + '(' + ','.join(self.params) + '))@' + str(self.lineno)
    def cg(self, w, view):
        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header('void ', self.identifier, '(', ','.join(self.params), ');')

        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source_block('void ', view, '::', self.identifier, '(', ','.join(self.params), ') {')
        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source('cppcms::translation_domain_scope _trs(out(),_domain_id);')

class AbstractTemplateDecl:
    '''abstract_template_decl : BEGIN_STATEMENT TMPL IDENTIFIER LPAREN expr_list RPAREN EQ ZERO END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.identifier = p[3]
        self.params = p[5]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'AbstractTemplateDecl(' + self.identifier + '(' + ','.join(self.params) + '))@' + str(self.lineno)
    def cg(self, w, view):
        w.header('#line %d "%s"' % (self.lineno, w.current_file))
        w.header('void ', self.identifier, '(', ','.join(self.params), ') = 0;')

