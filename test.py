
from cc import *
import ply.lex as lex
import ply.yacc as yacc

l = lex.lex()
y = yacc.yacc()

import sys

class CodeGenerator:
    header_indent = 0
    source_indent = 0
    variables = []
    is_template_context = False

    def __init__(self, h, src):
        self.header_file = h
        self.source_file = src

    def header(self, *parts):
        self.header_file.write('\t'*self.header_indent + ''.join(parts) + '\n')

    def header_block(self):
        self.header('{')
        self.header_indent += 1

    def header_leave(self):
        self.header_indent -= 1
        self.header('}')

    def source(self, *parts):
        self.source_file.write('\t'*self.source_indent + ''.join(parts) + '\n')

    def source_block(self):
        self.source('{')
        self.source_indent += 1

    def source_leave(self):
        self.source_indent -= 1
        self.source('}')

    def cpp(self, e):
        if self.is_template_context:
            self.source(e[1])
        else:
            self.header(e[1])

    def view(self, e):
        viewname = e[1][0]
        contenttype = e[1][1]
        extends = e[1][2]

        self.current_view = viewname

        self.header('struct ', viewname)
        if extends:
            self.header(': public ', extends)
        self.header_block()
        self.header(contenttype, ' &content;')
        self.header(viewname, '(std::ostream &_s, ', contenttype, ' &_content) : ', ( extends + '(_s,_content),' ) if extends else '', 'content(_content),_domain_id(0)')
        self.header_block()
        self.header('_domain_id=booster::locale::ios_info::get(_s).domain_id();')
        self.header_leave()
        for el in e[2]:
            if el[0] == 'CPP':
                self.cpp(el)
            elif el[0] == 'template':
                self.template(el)
            else:
                raise Exception('unexpected element ' + e[0])
        self.header_leave()

    def html(self, e):
        content = e[1].replace('\t','\\t').replace('"', '\\"')
        content = content.replace('\n', '\\n"\n' + '\t'*(self.source_indent + 2) + '"')
        self.source('out()<<"', content, '";')

    def variable(self, v):
        if '::' in v:
            return v # b/c it is scoped, therefore neither local nor in content
        name = re.search(r'(\w+)', v).group(1)
        if name in self.variables:
            return v
        return 'content.' + v

    def url(self, e):
        key = e[1]
        # TODO handle various expressions in using clause
        if e[2]:
            using_variables = [ self.variable(v) for v in e[2] ]
            using = ', ' + ','.join([ 'cppcms::filters::urlencode(' + v + ')' for v in using_variables ])
        else:
            using = ''

        self.source('content.app().mapper().map(out(),', key, using, ');')

    def if_(self, e):
        var, inverted = e[1]
        then = e[2]
        els = e[3]

        clause = ('!(' if inverted else '') + self.variable(var) + (')' if inverted else '')

        self.source('if (', clause, ')')
        self.source_block()
        self.html_block(then)
        self.source_leave()
        if els:
            self.source('else')
            self.source_block()
            self.html_block(els)
            self.source_leave()

    def foreach(self, e):
        var, container = e[1]
        pre = e[2]
        item = e[3]
        post = e[4]

        container = self.variable(container)

        self.source('if((', container, ').begin()!=(', container, ').end())')
        self.source_block()
        self.html_block(pre)
        self.source('for(CPPCMS_TYPEOF((', container, ').begin()) item_ptr=(', container, ').begin(),item_ptr_end=(', container, ').end();item_ptr!=item_ptr_end;++item_ptr)')
        self.source_block()
        self.source('CPPCMS_TYPEOF(*item_ptr) &', var, '=*item_ptr;')
        self.variables.append(var)
        self.html_block(item)
        self.variables.pop()
        self.source_leave()
        self.html_block(post)
        self.source_leave()

    def output_(self, e):
        var = self.variable(e[1])
        self.source('out()<<cppcms::filters::escape(', var, ');')

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
        self.is_template_context = True
        name = e[1]
        args = e[2]
        content = e[3]

        self.header('void ', name, '(', ','.join(args), ');')

        self.source('void ', self.current_view, '::', name, '(', ','.join(args), ')')
        self.source_block()
        self.source('cppcms::translation_domain_scope _trs(out(),_domain_id);')
        self.html_block(content)
        self.source_leave()
        self.is_template_context = False

    def skin(self, e):
        self.header('namespace ', e[1])
        self.header_block()
        self.source('namespace ', e[1])
        self.source_block()
        for el in e[2]:
            if el[0] == 'CPP':
                self.cpp(el)
            elif el[0] == 'view':
                self.view(el)
            else:
                raise Exception('unexpected element ' + e[0])
        self.header_leave()
        self.source_leave()
    
    def ast(self, ast):
        for e in ast:
            if e[0] == 'CPP':
                self.cpp(e)
            elif e[0] == 'skin':
                self.skin(e)
            else:
                raise Exception('unexpected element ' + e[0])

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

    def header_block(self):
        self.header('{')
        self.header_indent += 1

    def header_leave(self):
        self.header_indent -= 1
        self.header('}')

    def source(self, *parts):
        self.source_file.write('\t'*self.source_indent + ''.join(parts) + '\n')

    def source_block(self):
        self.source('{')
        self.source_indent += 1

    def source_leave(self):
        self.source_indent -= 1
        self.source('}')

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
    ##print(ast)
    ##sys.exit(0)
    #cg = CodeGenerator(h, sys.stdout)
    cg = Writer(h, sys.stdout)
    import os
    cg.ast(ast, os.path.realpath(sys.argv[1]))

