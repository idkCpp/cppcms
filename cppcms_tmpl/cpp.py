
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

def p_simple_expr(p):
    '''simple_expr : IDENTIFIER
                   | ITEM
                   | simple_expr MEMBER simple_expr
                   | simple_expr PTRMEMBER simple_expr
                   | simple_expr LPAREN expr_list RPAREN
                   | STAR simple_expr
                   | LPAREN simple_expr RPAREN
                   |'''
    if len(p) < 5:
        p[0] = ''.join(p[1:])
    else:
        p[0] = p[1] + p[2] + ','.join(p[3]) + p[4]

def p_expr(p):
    '''expr : IDENTIFIER
            | expr MEMBER expr
            | LPAREN expr RPAREN
            | EXCLAMATION_MARK expr
            | expr BITAND expr
            | expr AND expr
            | expr BITOR expr
            | expr OR expr
            | expr SAME expr
            | expr LPAREN expr_list RPAREN
            | STAR expr
            | ITEM'''
    if len(p) < 5:
        p[0] = ''.join(p[1:])
    else:
        p[0] = p[1] + p[2] + ','.join(p[3]) + p[4]
    #if len(p) == 2:
    #    p[0] = p[1]
    #elif len(p) == 3:
    #    p[0] = p[1] + p[2]
    #elif len(p) == 4:
    #    p[0] = p[1] + p[2] + p[3]

