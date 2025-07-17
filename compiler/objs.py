
from dataclasses import dataclass
import typing

import expr
import error
import sym
import util
import tree

@dataclass
class _put:
    target : expr.node
    expr : expr.node

    def infer(self, scope):
        scope.alloc_var(self.target)

    def generate(self, output, scope):
        self.expr.generate(output, scope)

        addr = util.var_to_addr(scope.ctx.locals[self.target])
        output('mov', f'[rbp-{addr}]', 'rax')
        
    
    @classmethod
    def parse(cls, stream, ctx):
        target = stream.pop()
        stream.expect("=")
        node = expr.parse(stream, ctx)

        return cls(target, node)


@dataclass
class _if:
    cond : expr.node
    body : typing.Any

    @classmethod
    def parse(cls, stream, ctx):
        cond = expr.parse(stream, ctx)
        body = parse(stream, ctx)
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
    def parse(cls, stream, ctx):
        return cls(stream.pop())


@dataclass
class _jump:
    label : str

    def generate(self, output, scope):
        scope.alloc_label(self.label, output)
        output('jmp', scope.labels[self.label])

    @classmethod
    def parse(cls, stream, ctx):
        return cls(stream.pop())



@dataclass
class _print:
    target : expr.node

    @classmethod
    def parse(cls, stream, ctx):
        return cls(expr.parse(stream, ctx))


    def generate(self, output, scope):
        self.target.generate(output, scope)
        output('call', 'print')


@dataclass
class _lam:
    body : 'tree.node'

    @classmethod
    def parse(cls, stream, ctx):
        body = tree.node.parse(stream, ctx)
        return cls(body)

    def generate(self, output, scope):
        skip_label = output.fresh_label()
        lam_label = output.fresh_label()

        output('jmp', skip_label)
        output.def_label(lam_label)

        self.body.generate(output)

        output('ret')
        output.def_label(skip_label)
        output('mov', 'rax', lam_label)
        output('mov', '[r10]', 'rax')
        output('inc', 'r10')


@dataclass
class _pull:
    target : str

    @classmethod
    def parse(cls, stream, ctx):
        return cls(stream.pop())

    def infer(self, scope):
        scope.ctx.alloc_var(self.target)


    def generate(self, output, scope):
        addr = util.var_to_addr(scope.ctx.vars[self.target])
        output('dec', 'r10')
        output('mov', 'rax', '[r10]')
        output('mov', f'[rbp-{addr}]', 'rax')



@dataclass
class _sub:
    node : expr.node

    @classmethod
    def parse(cls, stream, ctx):
        return cls(expr.parse(stream, ctx))

    def generate(self, output, scope):
        self.node.generate(output, scope)
        output('call', 'rax')



def parse(stream, ctx):
    iden = stream.pop()
    name = f"_{iden}"

    namespace = globals()
    if name not in namespace:
        error.stream_error(stream, f"Invalid statement name: {iden}")

    obj = namespace[name].parse(stream, ctx)
    if iden not in ('if'):
        stream.expect(sym.eos)

    return obj










