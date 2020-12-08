
from .common import sequence

class IfBlock:
    'html_statement : if_statement html_block end_block'
    def __init__(self, p):
        p[0] = self
        self.begin = p[1]
        self.then = p[2]
        self.end = p[3]
    def __repr__(self):
        return 'IfBlock(' + repr(self.begin) + ';' + repr(self.then) + ';' + repr(self.end) + ')'
    def cg(self, w):
        self.begin.cg(w)

        for e in self.then:
            e.cg(w)

        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave('} // endif')

class IfElseBlock:
    'html_statement : if_statement html_block else_statement html_block end_block'
    def __init__(self, p):
        p[0] = self
        self.begin = p[1]
        self.then = p[2]
        self.els = p[3]
        self.elseblock = p[4]
        self.end = p[5]
    def __repr__(self):
        return 'IfBlock(' + repr(self.begin) + ';' + repr(self.then) + ';' + repr(self.els) + ';' + repr(self.elseblock) + ';' + repr(self.end) + ')'
    def cg(self, w):
        self.begin.cg(w)

        for e in self.then:
            e.cg(w)

        w.source('#line %d "%s"' % (self.els.lineno, w.current_file))
        w.source_indent -= 1
        w.source('}else{')
        w.source_indent += 1

        for e in self.elseblock:
            e.cg(w)

        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave()

class IfStatement:
    '''if_statement : BEGIN_STATEMENT IF simple_expr END_STATEMENT
                    | BEGIN_STATEMENT IF NOT simple_expr END_STATEMENT
                    | BEGIN_STATEMENT IF LPAREN expr RPAREN END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        if len(p) == 5:
            self.inverted = False
            self.expression = p[3]
            self.direct = False
        elif len(p) == 6:
            self.inverted = True
            self.expression = p[4]
            self.direct = False
        else:
            self.inverted = False
            self.expression = p[4]
            self.direct = True
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'IfStatement(' + ('inverted:' if self.inverted else '') + self.expression + ')@' + str(self.lineno)
    def cg(self, w):
        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        if self.direct:
            clause = self.expression
        else:
            clause = w.variable(self.expression) if not self.inverted else '!(' + w.variable(self.expression) + ')'
        w.source_block('if(' + clause + ') {')

class ElseStatement:
    'else_statement : BEGIN_STATEMENT ELSE END_STATEMENT'
    def __init__(self, p):
        p[0] = self
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'ElseStatement@' + str(self.lineno)

class ForeachBlock:
    'html_statement : foreach_statement html_block item_statement html_block end_block html_block end_block'
    def __init__(self, p):
        p[0] = self
        self.begin = p[1]
        self.pre = p[2]
        self.item = p[4]
        self.post = p[6]
        self.end = p[7]
    def __repr__(self):
        return 'ForeachBlock(' + repr(self.begin) + ';' + repr(self.pre) + ';' + repr(self.item) + ';' + repr(self.post) + ';' + repr(self.end) + ')'
    def register(module):
        module['p_item'] = lambda p: None
        module['p_item'].__doc__ = 'item_statement : BEGIN_STATEMENT ITEM END_STATEMENT'
    def cg(self, w):
        w.source('#line %d "%s"' % (self.begin.lineno, w.current_file))
        w.source_block('if((', w.variable(self.begin.container), ').begin()!=(', w.variable(self.begin.container), ').end()) {')

        for e in self.pre:
            e.cg(w)

        self.begin.cg(w)

        for e in self.item:
            e.cg(w)

        w.variables.pop()

        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave('} // end of item')

        for e in self.post:
            e.cg(w)

        w.source('#line %d "%s"' % (self.end.lineno, w.current_file))
        w.source_leave()

class ForeachStatement:
    '''foreach_statement : BEGIN_STATEMENT FOREACH IDENTIFIER IN expr END_STATEMENT
                         | BEGIN_STATEMENT FOREACH ITEM IN expr END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.identifier = p[3]
        self.container = p[5]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'ForeachStatement(' + self.identifier + ';' + self.container + ')@' + str(self.lineno)
    def cg(self, w):

        stmt = 'for(CPPCMS_TYPEOF((%(c)s).begin()) %(i)s_ptr=(%(c)s).begin(),%(i)s_ptr_end=(%(c)s).end();%(i)s_ptr!=%(i)s_ptr_end;++%(i)s_ptr) {' % { 'i': self.identifier, 'c': w.variable(self.container) }

        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source_block(stmt)

        stmt = 'CPPCMS_TYPEOF(*%(i)s_ptr) &%(i)s=*%(i)s_ptr;' % { 'i': self.identifier }

        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source(stmt)

        w.variables.append(self.identifier)

class Html:
    '''html_statement : HTML
                      | NL'''
    def __init__(self, p):
        p[0] = self
        self.value = p[1]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'Html(' + self.value + ')@' + str(self.lineno)
    def cg(self, w):
        content = self.value.replace('\t','\\t').replace('"', '\\"')
        content = content.replace('\n', '\\n"\n' + '\t'*(w.source_indent + 2) + '"')
        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source('out()<<"', content, '";')

class OutputStatement:
    '''html_statement : BEGIN_STATEMENT EQ simple_expr filter_seq END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.expression = p[3]
        self.filter_seq = p[4]
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'OutputStatement(' + self.expression + ')@' + str(self.lineno)
    def cg(self, w):
        var = w.variable(self.expression)

        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        if self.filter_seq:
            w.source('out()<<' + ''.join(OutputStatement.nest_filter(var, self.filter_seq)) + ';')
        else:
            w.source('out()<<cppcms::filters::escape(', var, ');')
    def nest_filter(var, filter_seq):
        if len(filter_seq) > 0:
            res = []
            f = filter_seq[0]
            if f.is_extern:
                res.append('content.')
            else:
                res.append('cppcms::filters::')
            res.append(f.identifier)
            res.append('(')
            res += OutputStatement.nest_filter(var, filter_seq[1:])
            res.append(')')
            return res
        else:
            return [ var ]
    def register(module):
        module['p_filter_seq'] = lambda p: sequence(p)
        module['p_filter_seq'].__doc__ = '''filter_seq : filter_seq filter
                                                       |'''

class Filter:
    '''filter : BITOR IDENTIFIER optional_params
              | BITOR EXTERN IDENTIFIER optional_params'''
    def __init__(self, p):
        p[0] = self
        if len(p) == 4:
            self.is_extern = False
            self.identifier = p[2]
            self.parameter = p[3]
        else:
            self.is_extern = True
            self.identifier = p[3]
            self.parameter = p[4]
    def __repr__(self):
        return 'Filter(' + self.identifier + ';' + repr(self.parameter) + (';extern' if self.is_extern else '') + ')'
    def register(module):
        module['p_optional_params'] = lambda p: sequence(p)
        module['p_optional_params'].__doc__ = '''optional_params : LPAREN expr_list RPAREN
                                                                 |'''

class UrlStatement:
    '''html_statement : BEGIN_STATEMENT URL STRING END_STATEMENT
                      | BEGIN_STATEMENT URL STRING USING expr_list END_STATEMENT'''
    def __init__(self, p):
        p[0] = self
        self.key = p[3]
        self.using = p[5] if len(p) == 7 else None
        self.lineno = p.lineno(1)
    def __repr__(self):
        return 'UrlStatement(' + self.key + ( ';' + repr(self.using) if self.using else '' ) + ')@' + str(self.lineno)
    def cg(self, w):
        # TODO handle various expressions in using clause
        if self.using:
            using_variables = [ w.variable(v) for v in self.using ]
            using = ', ' + ','.join([ 'cppcms::filters::urlencode(' + v + ')' for v in using_variables ])
        else:
            using = ''

        w.source('#line %d "%s"' % (self.lineno, w.current_file))
        w.source('content.app().mapper().map(out(),', self.key, using, ');')

p_html_block_sequence = lambda p: sequence(p)
p_html_block_sequence.__doc__ = '''html_block : html_block html_statement
                                              |'''
def p_html_statement_from_cpp_decl(p):
    'html_statement : cpp_decl'
    p[0] = p[1]
