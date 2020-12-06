
def register(clz, mod):
    name = 'p_' + clz.__name__ + '_' + clz.__doc__.split(' ')[0]
    mod[name] = lambda p: clz(p)
    mod[name].__doc__ = clz.__doc__
    reg = getattr(clz, 'register', None)
    if reg:
        reg(mod) # call class-supplied register(module) method

