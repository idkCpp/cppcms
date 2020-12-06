
def non_empty_sequence(p):
    if type(p[1]) == list:
        p[0] = p[1] + [ p[2] ]
    else:
        p[0] = [ p[1] ]

def sequence(p):
    if len(p) == 3:
        p[0] = p[1] + [ p[2] ]
    elif len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = []

