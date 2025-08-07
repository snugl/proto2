
from dataclasses import dataclass

import sym
import error

@dataclass
class node:
    kind : str
    content : str
    left  : 'node | None' = None
    right : 'node | None' = None

    def infer(self, ctx):
        #only variable can infer
        if self.kind == 'var':
            ctx.allocate_variable(self.content)

        if self.kind == 'op' and self.content == sym.assign:
            if type(self.left) is node:
                self.left.infer(ctx)

    #generate reads from acc
    def write(self, output, ctx):
        #either variable or dot operator

        match self.kind:
            case 'var' if self.content in ctx.vars: #might be global constant
                output('store', ctx.vars[self.content])
            case 'op' if self.content == sym.op_dot and \
                    type(self.left ) is node and \
                    type(self.right) is node :
                #preserve original
                output('push') 

                #compute target addr
                self.right.generate(output, ctx)
                output('push')
                self.left.generate(output, ctx)
                output('add')

                #perform enref
                output('ref')
                
            case x:
                error.error(f"Unable to write to expression {self.content} of type {x}");
                

     
    #generate outputs to acc
    def generate(self, output, ctx):
        def bool_normalize():
            output('push')
            output('const', 1)
            output('and')


        vars = ctx.vars
        match self.kind:
            case 'num':
                output('const', self.content)
            case 'var' if self.content in vars:
                output('load', vars[self.content])
            case 'var' if self.content in ctx.tree.consts:
                output('const', ctx.tree.consts[self.content])
            case 'op' if type(self.left) is node and type(self.right) is node:
                oper = self.content

                if oper != sym.op_assign:
                    self.right.generate(output, ctx)
                    output('push')
                    self.left.generate(output, ctx)

                match oper:
                    case sym.op_assign:
                        self.right.generate(output, ctx)
                        self.left.write(output, ctx)

                    case sym.op_add:     output('add'),
                    case sym.op_sub:     output('sub'),
                    case sym.op_bit_or:  output('or')
                    case sym.op_bit_and: output('and')
                    case sym.op_gt :     output('greater'), #acc is greater
                    case sym.op_lt :     output('lesser'),  #acc is lesser
                    case sym.op_eq :     output('equal'),
                    case sym.op_neq:     output('nequal'),
                    case sym.op_mul:     output('mul'),


                    case sym.op_dot:
                        output('add')
                        output('deref')

                    case sym.op_ge:
                        output('inc') #or equal
                        output('greater')
                    case sym.op_le:
                        output('dec') #or equal
                        output('lesser')

                    case sym.op_boo_or:
                        output('or')
                        bool_normalize()

                    case sym.op_boo_and:
                        output('and')
                        bool_normalize()


                    case sym.op_pre_add:
                        output('add')
                        self.left.write(output, ctx)

                    case sym.op_pre_sub:
                        output('sub')
                        self.left.write(output, ctx)


                    case sym.op_post_add:
                        output('add')
                        self.left.write(output, ctx)
                        output('sub')

                    case sym.op_post_sub:
                        output('sub')
                        self.left.write(output, ctx)
                        output('add')



            case 'string':
                output('string', f"'{self.content}'")

            case 'char':
                output('const', ord(self.content))

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


