
from dataclasses import dataclass
from dataclasses import field
import os
import typing

import expr
import sym
import emission
import tree
import abstract
import error

@dataclass
class _debug:
    target : expr.node

    @classmethod
    def parse(cls, stream):
        return cls(expr.parse(stream))

    def generate(self, output, ctx):
        self.target.generate(output, ctx)
        output('debug')

@dataclass
class _pull:
    target : expr.node

    @classmethod
    def parse(cls, stream):
        return cls(expr.parse(stream))

    def infer(self, ctx):
        self.target.infer(ctx)

    def generate(self, output, ctx):
        output('pull')
        self.target.write(output, ctx)

@dataclass
class _push:
    target : expr.node

    @classmethod
    def parse(cls, stream):
        return cls(expr.parse(stream))

    def generate(self, output, ctx):
        self.target.generate(output, ctx)
        output('push')




@dataclass
class _use:
    path : str

    @classmethod
    def parse(cls, stream):
        path = stream.pop()
        return cls(path = path)

    #called by tree.node itself
    def expand(self, root):
        module_tree = tree.prepare(self.path)
        root.inject(module_tree)



@dataclass
class _put:
    target : expr.node
    @classmethod
    def parse(cls, stream):
        target = expr.parse(stream)
        return cls(target)

    def infer(self, ctx):
        self.target.infer(ctx)

    def generate(self, output, ctx):
        self.target.generate(output, ctx)



@dataclass
class _lab:
    label : str | None
    @classmethod
    def parse(cls, stream):
        return cls(
            stream.pop() if 
            stream.peek() != sym.eos 
            else None
        )

    def generate(self, output, ctx):
        output.define_local_label(self.label, ctx.routine.name)
        

@dataclass
class _jump:
    label : str | None
    cond  : expr.node | None
    @classmethod
    def parse(cls, stream):
        label = (stream.pop() if
            stream.peek() not in (sym.eos, sym.binding)
            else None)
        
        if stream.peek() != sym.binding:
            return cls(label, cond=None)

        stream.expect(sym.binding)
        cond = expr.parse(stream)
        return cls(label, cond)

    def generate(self, output, ctx):
        target_label = emission.reference(self.label, ctx.routine.name, output, entry=False)
        if self.cond is None:
            output('jump', target_label)

        else:
            self.cond.generate(output, ctx)
            output('branch', target_label)

@dataclass
class _sub:
    target : str
    imap : dict[str, expr.node] = field(default_factory=lambda: {})

    @classmethod
    def parse(cls, stream):
        target = stream.pop()

        if stream.peek() == sym.eos:
            return cls(target)

        #interface
        imap = {}
        stream.expect(sym.param_start)
        while stream.peek() != sym.param_end:
            #callee side
            internal = stream.pop()

            #caller side
            if stream.peek() == sym.binding:
                stream.expect(sym.binding)
                external = expr.parse(stream) #if stream.peek() != ";" else None
            else: #auto infer mapped external expression
                external = expr.node(
                    kind = 'var',
                    content = internal
                )

            #optional delimiter
            if stream.peek() == ",":
                stream.pop()

            imap[internal] = external
        stream.expect(sym.param_end)

        return cls(target, imap)

    def infer(self, ctx):
        target_obj = ctx.tree.get_routine(self.target)
        pinter = target_obj.pinter

        for binding_name in pinter.out_param:
            if binding_name not in self.imap:
                error.error(f"Required out-parameter '{binding_name}' in call to routine {self.target} not bound")
            variable_name = self.imap[binding_name].content
            ctx.allocate_variable(variable_name)


    def generate(self, output, ctx):
        target_obj = ctx.tree.get_routine(self.target)
        pinter = target_obj.pinter

        #construct in-paramter space
        #THE ORDER IS IMPORTANT
        for param in pinter.in_param:
            if param not in self.imap:
                error.error(f"Required in-parameter '{param}' in call to routine {self.target} not bound")

            self.imap[param].generate(output, ctx)
            output('push')

        #construct out-parameter space
        output('alloc', len(pinter.out_param))

        #routine_origin = ctx.tree.lookup_routine_origin(target_obj.name)
        routine_reference = emission.reference(target_obj.name, None, output, entry=True)
        output('call', routine_reference)

        #deconstruct out-parameters
        for param in pinter.out_param[::-1]:
            output('pull')
            self.imap[param].write(output, ctx)

        #deconstruct in-paramters
        output('free', len(pinter.in_param))

@dataclass
class _trans:
    size   : expr.node
    target : expr.node #expr has to be writeable

    @classmethod
    def parse(cls, stream):
        size = expr.parse(stream)
        stream.expect(sym.binding)
        target = expr.parse(stream)

        return cls(size, target)

    def infer(self, ctx):
       self.target.infer(ctx)

    def generate(self, output, ctx):
        pass


@dataclass
class _defer:
    obj: expr.node

    @classmethod
    def parse(cls, stream):
        obj = parse(stream)
        return cls(obj)

    def generate(self, output, ctx):
        super = tree.node(
            subs = [self.obj],
            consts = {},
        )
        ctx.routine.sapling.inject(super)



@dataclass
class _rout:
    #parse
    name  : str = ""
    sapling : 'tree.node' = field(default_factory=lambda: tree.node())

    pinter : abstract.param_interface = field(default_factory=lambda: abstract.param_interface())

    #local compilation context
    @dataclass
    class _ctx:
        vars : dict[str, int]
        var_allocer : typing.Iterator
        tree : 'tree.node'
        routine : '_rout'

        def allocate_variable(self, name):
            if name not in self.vars.keys():
                self.vars[name] = next(self.var_allocer)

    #collect and emit dependencies of routine (recursivly *the horror*)
    def dependencies(self, output, tree):
        def walk(sapling):
            nonlocal output, tree
            for node in sapling:
                if type(node) is _sub:
                    depend = tree.get_routine(node.target)
                    depend.generate(output, tree)

        walk(self.sapling) 


    def generate(self, output, tree):
        #make sure routine is only generated once
        if output.check_routine_defined(self.name):
            return

        output.define_routine(self.name)

        #build compilation context
        ctx = self._ctx(
            vars = {},
            var_allocer = iter(range(16)),
            tree = tree,
            routine = self
        )

        #generate and interlace interface binding
        ctx.vars.update(self.pinter.generate_variable_binding())

        #infer variables
        self.sapling.infer(ctx)

        #reserve local stack space for variables
        var_count = next(ctx.var_allocer)
        output.annotate(f'"rout {self.name}')
        output.annotate(f'"\tvars: {list(ctx.vars)}')
        output("alloc", var_count)


        #generate routine behavior
        self.sapling.generate(output, ctx)
        #for node in self.sapling:
        #    node.generate(output, ctx)

        #free variable space
        output("free", var_count)

        output('return')

        #resolve dependencies
        self.dependencies(output, tree)



    @classmethod
    def parse(cls, stream):
        self = cls()
        self.name = stream.pop()
        
        #interface
        if stream.peek() == sym.param_start:
            stream.expect(sym.param_start)
            while stream.peek() != sym.param_end:
                match stream.pop():
                    case "in":  self.pinter.add_in(stream.pop())
                    case "out": self.pinter.add_out(stream.pop())
                stream.expect(sym.eos)
            stream.expect(sym.param_end)

        stream.expect(sym.block_start)
        self.sapling = tree.parse(stream)
        stream.expect(sym.block_end)

        return self


@dataclass
class _seq:
    name : str
    fields : list[str]

    @classmethod
    def parse(cls, stream):
        name = stream.pop()
        fields = []

        stream.expect(sym.block_start)
        while stream.peek() != sym.block_end:
            fields.append(stream.pop())
            stream.maybe(",") #comma delims are optional
        
        stream.expect(sym.block_end)

        return cls(
            name,
            fields
        )

    def get_size(self):
        return len(self.fields)

    def render_constants(self):
        consts = {}

        #seq length by name
        consts[self.name] = self.get_size()

        #seq field offsets by scoped name
        for offset, field_name  in enumerate(self.fields):
            name = f"{self.name}::{field_name}"
            consts[name] = offset

        return consts



def parse(stream):
    iden = stream.pop()
    name = f"_{iden}"

    namespace = globals()
    if name not in namespace:
        error.stream_error(stream, f"Invalid statement name: {iden}")

    obj = namespace[name].parse(stream)
    if iden not in ("rout", "seq", "defer"):
        stream.expect(sym.eos)

    return obj
