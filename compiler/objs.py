
from dataclasses import dataclass

import expr
import error
import sym

@dataclass
class _put:
    lhs : expr.node
    rhs : expr.node
    
    @classmethod
    def parse(cls, stream):
        lhs = stream.pop()
        stream.expect("=")
        rhs = expr.parse(stream)

        return cls(lhs, rhs)

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










