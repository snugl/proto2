
from dataclasses import dataclass
from dataclasses import field
import typing
import itertools

import objs



@dataclass
class Node:
    subs   : list['Node']   = field(default_factory=lambda: [])
    locals : dict[str, int] = field(default_factory=lambda: {})

    var_allocer : typing.Iterator = field(default_factory=lambda: itertools.count(0))

    def alloc_var(self, name):
        if name not in self.locals:
            self.locals[name] = next(self.var_allocer)

    def infer(self):
        for sub in self.subs:
            if hasattr(sub, 'infer'):
                sub.infer(self)

    def generate(self, output):
        local_words = next(self.var_allocer)
        local_bytes = local_words * 8 # 1 word => 8 bytes

        #scope setup
        output('push', 'rbp')
        output('mov', 'rbp', 'rsp')
        output('sub', 'rsp', local_bytes)

        for sub in self.subs:
            sub.generate(output, self)

        #scope teardown
        output('add', 'rsp', local_bytes)
        output('mov', 'rsp', 'rbp')
        output('pop', 'rbp')


    @classmethod
    def parse(cls, stream, root=False):
        self = cls()

        if not root: stream.expect("{")

        while stream.has() and stream.peek() != "}":
            self.subs.append(objs.parse(stream))

        if not root: stream.expect("}")

        return self

