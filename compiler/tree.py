
from dataclasses import dataclass
from dataclasses import field
import typing
import itertools

import objs
import error
import emission



@dataclass
class node:
    ctx    : 'ctx'
    subs   : list['node']   = field(default_factory=lambda: [])
    labels : dict[str, str] = field(default_factory=lambda: {})

    


    def alloc_label(self, name, output):
        if name not in self.labels:
            real = output.fresh_label()
            self.labels[name] = real



    def infer(self, scope):
        for sub in self.subs:
            if hasattr(sub, 'infer'):
                sub.infer(self)

    def generate(self, output):
        for sub in self.subs:
            sub.generate(output, self)


    @classmethod
    def parse(cls, stream, ctx, root=False):
        self = cls(ctx)

        if not root: stream.expect("{")

        while stream.has() and stream.peek() != "}":
            self.subs.append(objs.parse(stream, ctx))

        if not root: stream.expect("}")

        return self



@dataclass
class ctx:
    root   : node               = None
    output : emission.buffer    = None

    vars        : dict[str, int]  = field(default_factory=lambda: {})
    var_allocer : typing.Iterator = field(default_factory=lambda: itertools.count(0))

    def alloc_var(self, name):
        if name not in self.vars:
            self.vars[name] = next(self.var_allocer)

    def var_addr(self, name):
        if name not in self.vars:
            error.error(f"Unable to resolve variable name {name}")

        addr = self.vars[name] * 8
        return f'vars + {addr}'

    @classmethod
    def parse(cls, stream):
        self = cls()
        self.root = node.parse(stream, self, root=True)
        self.output = emission.buffer()

        return self


    def compile(self):
        self.root.infer(self.root)
        self.root.generate(self.output)

        #exit syscall
        self.output('mov', 'rax', 60)
        self.output('mov', 'rdi', 0)
        self.output('syscall')

        var_count = next(self.var_allocer)

        self.output.finalize(var_count)
        self.output.assemble('main')


    def render(self):
        return self.output.render()



