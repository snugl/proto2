
from dataclasses import dataclass

import expr
import error
import sym

@dataclass
class _put:
    target : expr.node
    expr : expr.node

    def infer(self, scope):
        scope.alloc_var(self.target)
    
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










