
from dataclasses import dataclass

import sym
import error

@dataclass
class node:
    kind : str
    content : str
    left  : 'node | None' = None
    right : 'node | None' = None


    def infer(self, scope):
        #only variable can infer
        if self.kind == 'var':
            scope.ctx.alloc_var(self.content)

    #generate read from rax
    def gen_read(self, output, scope):
        match self.kind:
            case 'var' if self.content in scope.ctx.vars:
                addr = scope.ctx.var_addr(self.content)
                output('mov', f'[{addr}]', 'rax')
            case 'op' if self.content == sym.op_dot:
                error.error('TODO: implement write to dot operator')

            case x:
                error.error(f"Unable to write to expression {self.content} of type {x}");

     
    #generate write to rax
    def gen_write(self, output, scope):
        vars = scope.ctx.vars
        match self.kind:
            case 'num':
                output('mov', 'rax', self.content)
            case 'var' if self.content in vars:
                addr = scope.ctx.var_addr(self.content)
                output('mov', 'rax', f'[{addr}]')
            case 'op' if type(self.left) is node and type(self.right) is node:
                self.right.gen_write(output, scope)
                output('push', 'rax')
                self.left.gen_write(output, scope)
                output('pop', 'rbx')

                op = self.content
                if op in sym.op_cond:
                    output('cmp', 'rax', 'rbx')

                match self.content:
                    case sym.op_add: output('add', 'rax', 'rbx'),
                    case sym.op_sub: output('sub', 'rax', 'rbx'),
                    case sym.op_mul: output('mul', 'rax', 'rbx'),

                    case sym.op_gt:   output('setg' , 'al'),
                    case sym.op_lt:   output('setl' , 'al'),
                    case sym.op_ge:   output('setge', 'al'),
                    case sym.op_le:   output('setle', 'al'),
                    case sym.op_eq:   output('sete' , 'al'),
                    case sym.op_neq:  output('setne', 'al'),

                    case sym.op_dot:  output('mov', 'rax', '[rax + rbx]')

                    case sym.op_bit_and: output('and', 'rax', 'rbx')
                    case sym.op_boo_and: output('and', 'rax', 'rbx')


                if op in sym.op_cond + sym.op_bool: #normalize
                    output('and', 'rax', '0x01')


            case 'string':
                str_addr = output.alloc_string(self.content)
                output('mov', 'rax', str_addr)


            case x:
                error.error(f"Unable to evaluate to expression of type {x} and content '{self.content}'");



def parse_expr(stream, prec_level) -> node:
    left = parse_higher(stream, prec_level)

    if str(stream.peek()) not in sym.prec[prec_level]:
        return left


    op = stream.pop()
    right = parse_expr(stream, prec_level)
    return node(
        kind = 'op',
        content = op,
        left = left,
        right = right
    )

#parse at higher precedence level
def parse_higher(stream, prec_level) -> node:
    prec_level_next = prec_level + 1
    if prec_level_next < len(sym.prec):
        return parse_expr(stream, prec_level_next)
    else:
        return parse_terminal(stream)

def parse_terminal(stream) -> node:
    match stream.pop_raw():
        case x if x.content == '(' and x.kind == 'open_paran':
            expr = parse_expr(stream, 0)
            stream.expect(")")
            return expr
        case x if x.kind == 'numb':
            return node(
                kind = 'num',
                content = int(x.content)
            )
        case x if x.kind == 'iden':
            return node(
                kind = 'var',
                content = x.content
            )
        case x if x.kind == 'quote':
            return node(
                kind = 'string',
                content = x.content
            )
        case x if x.kind == 'char_lit':
            return node(
                kind = 'char',
                content = x.content
            )
        case x:
            error.stream_error(stream, f"Unable to parse terminal '{x}' of type {x.kind}")


def parse(stream, ctx) -> node:
    return parse_expr(stream, 0)



