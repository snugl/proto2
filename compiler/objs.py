
from dataclasses import dataclass
import typing

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
class _if:
    cond : expr.node
    body : typing.Any

    @classmethod
    def parse(cls, stream):
        cond = expr.parse(stream)
        body = parse(stream)
        return cls(cond, body)

    def generate(self, output, scope):
        fresh = output.fresh_label()

        self.cond.generate(output, scope)
        output('jz', fresh)
        self.body.generate(output, scope)
        output.def_label(fresh)



@dataclass
class _lab:
    label : str

    def generate(self, output, scope):
        scope.alloc_label(self.label, output)
        output.def_label(scope.labels[self.label])


    @classmethod
    def parse(cls, stream):
        return cls(stream.pop())


@dataclass
class _jump:
    label : str

    def generate(self, output, scope):
        scope.alloc_label(self.label, output)
        output('jmp', scope.labels[self.label])

    @classmethod
    def parse(cls, stream):
        return cls(stream.pop())



@dataclass
class _print:
    target : expr.node

    @classmethod
    def parse(cls, stream):
        return cls(expr.parse(stream))


    def generate(self, output, scope):
        self.target.generate(output, scope)
        output('call', 'print')




def parse(stream):
    iden = stream.pop()
    name = f"_{iden}"

    namespace = globals()
    if name not in namespace:
        error.stream_error(stream, f"Invalid statement name: {iden}")

    obj = namespace[name].parse(stream)
    if iden not in ('if'):
        stream.expect(sym.eos)

    return obj










