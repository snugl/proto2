
from dataclasses import dataclass

import expr
import error
import sym
import util

@dataclass
class _put:
    target : expr.node
    expr : expr.node

    def infer(self, scope):
        scope.alloc_var(self.target)

    def generate(self, output, scope):
        self.expr.generate(output, scope)

        addr = util.var_to_addr(scope.locals[self.target])
        output('mov', f'[rbp-{addr}]', 'rax')
        
    
    @classmethod
    def parse(cls, stream):
        target = stream.pop()
        stream.expect("=")
        node = expr.parse(stream)

        return cls(target, node)



@dataclass
class _print:
    target : expr.node

    @classmethod
    def parse(cls, stream):
        return cls(expr.parse(stream))


    def generate(self, output, scope):
        self.target.generate(output, scope)
        output('push', 'rax')
        output('call', 'print')
        output('add', 'rsp', 8)




def parse(stream):
    iden = stream.pop()
    name = f"_{iden}"

    namespace = globals()
    if name not in namespace:
        error.stream_error(stream, f"Invalid statement name: {iden}")

    obj = namespace[name].parse(stream)
    #if iden not in ():
    stream.expect(sym.eos)

    return obj










