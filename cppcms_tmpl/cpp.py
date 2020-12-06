
def p_possibly_scoped_identifier(p):
    '''possibly_scoped_identifier : possibly_scoped_identifier SCOPE IDENTIFIER
                                  | IDENTIFIER'''
    if len(p) == 4:
        p[0] = p[1] + '::' + p[3]
    else:
        p[0] = p[1]

def p_expr_list(p):
    '''expr_list : expr_list COMMA expr
                 | expr
                 |'''
    if len(p) == 4:
        p[0] = p[1] + [ p[3] ]
    elif len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = []

def p_expr(p):
    '''expr : IDENTIFIER
            | expr MEMBER expr
            | STAR expr
            | ITEM'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]

