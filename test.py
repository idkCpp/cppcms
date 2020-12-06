
from cc import *
import ply.lex as lex
import ply.yacc as yacc

l = lex.lex()
y = yacc.yacc()

import sys

class CodeGenerator:
    indent = 0
    variables = []

    def output(self, *parts):
        print('\t'*self.indent + ''.join(parts))

    def block(self):
        self.output('{')
        self.indent += 1

    def leave(self):
        self.indent -= 1
        self.output('}')

    def cpp(self, e):
        self.output(e[1])

    def view(self, e):
        viewname = e[1][0]
        contenttype = e[1][1]
        extends = e[1][2]

        self.current_view = viewname

        self.output('struct ', viewname)
        if extends:
            self.output(': public ', extends)
        self.block()
        self.output(contenttype, ' &content;')
        self.output(viewname, '(std::ostream &_s, ', contenttype, ' &_content) : ', ( extends + '(_s,_content),' ) if extends else '', 'content(_content),_domain_id(0)')
        self.block()
        self.output('_domain_id=booster::locale::ios_info::get(_s).domain_id();')
        self.leave()
        for el in e[2]:
            if el[0] == 'CPP':
                self.cpp(el)
            elif el[0] == 'template':
                self.template(el)
            else:
                raise Exception('unexpected element ' + e[0])
        self.leave()

    def html(self, e):
        content = e[1].replace('\n','\\n').replace('\t','\\t').replace('"', '\\"')
        self.output('out()<<"', content, '";')

    def variable(self, v):
        if v in self.variables:
            return v
        return 'content.' + v

    def url(self, e):
        key = e[1]
        # TODO handle various expressions in using clause
        if e[2]:
            using = [ self.variable(v) for v in e[2] ]
        else:
            using = []
        self.output('content.app().mapper().map(out(),', key, ', ', ','.join([ 'cppcms::filters::urlencode(' + v + ')' for v in using ]), ');')

    def if_(self, e):
        clause = e[1]
        then = e[2]
        els = e[3]

        self.output('if (', clause, ')')
        self.block()
        self.html_block(then)
        self.leave()
        if els:
            self.output('else')
            self.block()
            self.html_block(els)
            self.leave()

    def foreach(self, e):
        var, container = e[1]
        pre = e[2]
        item = e[3]
        post = e[4]

        container = self.variable(container)

        self.output('if((', container, ').begin()!=(', container, ').end())')
        self.block()
        self.html_block(pre)
        self.output('for(CPPCMS_TYPEOF((', container, ').begin()) item_ptr=(', container, ').begin(),item_ptr_end=(', container, ').end();item_ptr!=item_ptr_end;++item_ptr)')
        self.block()
        self.output('CPPCMS_TYPEOF(*item_ptr) &', var, '=*item_ptr;')
        self.html_block(item)
        self.leave()
        self.html_block(post)
        self.leave()

    def output_(self, e):
        var = self.variable(e[1])
        self.output('out()<<cppcms::filters::escape(', var, ');')

    def html_block(self, e):
        for el in e:
            if el[0] == 'CPP':
                self.cpp(el)
            elif el[0] == 'html':
                self.html(el)
            elif el[0] == 'url':
                self.url(el)
            elif el[0] == 'if':
                self.if_(el)
            elif el[0] == 'foreach':
                self.foreach(el)
            elif el[0] == 'output':
                self.output_(el)
            else:
                raise Exception('unexpected element ' + el[0])

    def template(self, e):
        name = e[1]
        args = e[2]
        content = e[3]
        
        self.output('void ', name, '(', ','.join(args), ')')
        self.block()
        self.output('cppcms::translation_domain_scope _trs(out(),_domain_id);')
        self.html_block(content)
        self.leave()

    def skin(self, e):
        self.output('namespace ', e[1])
        self.block()
        for el in e[2]:
            if el[0] == 'CPP':
                self.cpp(el)
            elif el[0] == 'view':
                self.view(el)
            else:
                raise Exception('unexpected element ' + e[0])
        self.leave()
    
    def ast(self, ast):
        for e in ast:
            if e[0] == 'CPP':
                self.cpp(e)
            elif e[0] == 'skin':
                self.skin(e)
            else:
                raise Exception('unexpected element ' + e[0])

with open(sys.argv[1], 'r') as f:
    ast = y.parse(f.read())
    cg = CodeGenerator()
    cg.ast(ast)

