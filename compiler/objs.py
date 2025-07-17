
from dataclasses import dataclass
import typing

import expr
import error
import sym
import tree

@dataclass
class _put:
    target : expr.node
    expr : expr.node

    def infer(self, scope):
        scope.ctx.alloc_var(self.target)

    def generate(self, output, scope):
        self.expr.gen_write(output, scope)

        addr = scope.ctx.var_addr(self.target)
        output('mov', f'[{addr}]', 'rax')
        
    
    @classmethod
    def parse(cls, stream, ctx):
        target = stream.pop()
        stream.expect("=")
        node = expr.parse(stream, ctx)

        return cls(target, node)



@dataclass
class _asm:
    content : str

    @classmethod
    def parse(cls, stream, ctx):
        return cls(stream.pop())

    def generate(self, output, scope):
        output(self.content)


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

        self.cond.gen_write(output, scope)
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
        self.target.gen_write(output, scope)
        output('call', 'print')


@dataclass
class _lam:
    body : 'tree.node'

    @classmethod
    def parse(cls, stream, ctx):
        body = tree.node.parse(stream, ctx)
        return cls(body)

    def infer(self, scope):
        self.body.infer(scope)

    def generate(self, output, scope):
        skip_label = output.fresh_label()
        lam_label = output.fresh_label()

        output('push', lam_label)
        output('jmp', skip_label)
        output.def_label(lam_label)

        self.body.generate(output)

        output('ret')
        output.def_label(skip_label)

@dataclass
class _rout:
    name : str
    body : 'tree.node'

    @classmethod
    def parse(cls, stream, ctx):
        name = stream.pop()
        body = tree.node.parse(stream, ctx)
        return cls(name, body)

    def infer(self, scope):
        scope.ctx.alloc_var(self.name)
        self.body.infer(scope)

    def generate(self, output, scope):
        skip_label = output.fresh_label()
        lam_label = output.fresh_label()

        addr = scope.ctx.var_addr(self.name)
        output('mov', f'qword [{addr}]', lam_label)
        output('jmp', skip_label)
        output.def_label(lam_label)

        self.body.generate(output)

        output('ret')
        output.def_label(skip_label)



@dataclass
class _pull:
    target : expr.node

    @classmethod
    def parse(cls, stream, ctx):
        return cls(expr.parse(stream, ctx))

    def infer(self, scope):
        self.target.infer(scope)

    def generate(self, output, scope):
        output('pop', 'rax')
        self.target.gen_read(output, scope)

@dataclass
class _push:
    target : expr.node

    @classmethod
    def parse(cls, stream, ctx):
        return cls(expr.parse(stream, ctx))

    def infer(self, scope):
        self.target.infer(scope)

    def generate(self, output, scope):
        self.target.gen_write(output, scope)
        output('push', 'rax')

    



@dataclass
class _sub:
    node : expr.node

    @classmethod
    def parse(cls, stream, ctx):
        return cls(expr.parse(stream, ctx))

    def generate(self, output, scope):
        self.node.gen_write(output, scope)
        output('call', 'rax')



def parse(stream, ctx):
    iden = stream.pop()
    name = f"_{iden}"

    namespace = globals()
    if name not in namespace:
        error.stream_error(stream, f"Invalid statement name: {iden}")

    obj = namespace[name].parse(stream, ctx)
    if iden not in ('if', 'rout'):
        stream.expect(sym.eos)

    return obj










