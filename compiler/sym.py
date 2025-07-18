assign = '='
eos = ';'
param_start = '('
param_end   = ')'
block_start = '{'
block_end   = '}'

op_add = '+'
op_sub = '-'
op_gt  = '>'
op_lt  = '<'
op_ge  = '>='
op_le  = '<='
op_eq  = '=='
op_neq = '!='
op_mul = '*'
op_dot = '.'
op_bit_and = '&'
op_bit_or  = '|'
op_boo_and = '&&'
op_boo_or  = '||'


op_bool = (
    op_boo_and,
    op_boo_or,
)


op_cond = (
    op_lt,
    op_gt,
    op_le,
    op_ge,
    op_eq,
    op_neq,
)


#precedence
prec = [
    (op_boo_and, op_boo_or),
    (op_gt, op_lt, op_eq, op_neq, op_ge, op_le),
    (op_bit_and, op_bit_or),
    (op_add, op_sub),
    (op_mul),
    (op_dot),
]

ops = [
    value for name, value in
    list(globals().items()) #list() to make copy
    if name.startswith('op_')
]




