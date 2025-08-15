
from dataclasses import dataclass
from dataclasses import field

import objs
import sym
import error
import lex



@dataclass
class node:
    subs   : list['node'] = field(default_factory=lambda: [])
    consts : dict[str, int] = field(default_factory=lambda: {})

    def __len__(self):
        return len(self.subs)

    def __getitem__(self, key):
        return self.subs[key]

    def inject(self, other):
        self.subs += other.subs
        self.consts.update(other.consts)


    def expand(self):
        for sub in self.subs:
            if type(sub) is objs._use:
                sub.expand(self)

    def get_routine(self, name) -> objs._rout:
        for sub in self.subs:
            if sub is None: continue
            if type(sub) is not objs._rout: continue
            if sub.name == name:
                return sub

        error.error(f"Unable to resolve routine name: {name}")



    #only applies to root.
    #so all root tree scopes should contain consts,
    #making them accessable to local compilation context objs._rout._ctx
    def render_constants(self):
        for sub in self.subs:
            t = type(sub)
            if t is objs._seq or t is objs._const:
                self.consts.update(sub.render_constants())



    def generate(self, output, ctx):
        for node in self.subs:
            node.generate(output, ctx)

    def infer(self, ctx):
        for node in self.subs:
            if hasattr(node, "infer"):
                node.infer(ctx)
            
    
def parse(stream):
    root = node()

    while stream.has() and stream.peek() != '}':
        root.subs.append(objs.parse(stream))

    return root



#lex, parse, expand imports
def prepare(path):
    stream = lex.tokenize(path)
    root = parse(stream)

    root.render_constants()
    root.expand()


    return root
