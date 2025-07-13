
from dataclasses import dataclass

import sym
import error
import util

@dataclass
class node:
    kind : str
    content : str
    left  : 'node | None' = None
    right : 'node | None' = None

     
    #generate outputs to acc
    def generate(self, output, scope):
        vars = scope.locals
        match self.kind:
            case 'num':
                output('mov', 'rax', self.content)
            case 'var' if self.content in vars:
                addr = util.var_to_addr(vars[self.content])
                output('mov', 'rax', f'[rbp-{addr}]')
            case 'op' if type(self.left) is node and type(self.right) is node:
                self.right.generate(output, scope)
                output('push', 'rax')
                self.left.generate(output, scope)
                output('pop', 'rbx')

                match self.content:
                    case sym.op_add: output('add', 'rax', 'rbx'),

            case x:
                error.error(f"Unable to evaluate to expression of type {x} and content '{self.content}'");



def parse_expr(stream, prec_level) -> node:
    left = parse_higher(stream, prec_level)

    if str(stream.peek()) not in sym.prec[prec_level]:
        return left

    op = stream.pop()
    right = parse_higher(stream, prec_level)
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


def parse(stream) -> node:
    return parse_expr(stream, 0)



