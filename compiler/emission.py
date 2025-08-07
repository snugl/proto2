
from dataclasses import dataclass
from dataclasses import field

import error


@dataclass
class command: 
    inst : str
    arg : str | None

    def __str__(self):
        str_arg = str(self.arg) if self.arg is not None else ''
        return f"{self.inst} {str_arg}".strip()



@dataclass
#refers to point (address) in program
class reference:
    name     : str | None
    routine  : str | None
    emission : 'output'
    entry    : bool

    def __str__(self):
        return str(
            self.emission.lookup_routine(self.name) if self.entry else
            self.emission.lookup_local_label(self.name, self.routine)
        )




@dataclass
class anno:
    msg : str

    def __str__(self):
        return self.msg

@dataclass
class output:
    seq : list[command | anno] = field(default_factory=lambda: []) 
    addr : int = 0

    # maps definition to address
    definition_mapper : dict[tuple[str, str], int] = field(default_factory=lambda: {})
    routine_mapper    : dict[str, int]             = field(default_factory=lambda: {})

    #the link header gets put at the start of the build executable.
    #it consists of 2 commands to call the main routine:
    #   call <address of main>
    #   halt
    link_header_size = 2


    def annotate(self, msg):
        self.seq.append(anno(msg))

    def __call__(self, inst, arg=None):
        cmd = command(inst, arg)
        self.seq.append(cmd)
        self.addr += 1

    def define_local_label(self, name, routine):
        key = (name, routine)
        if key in self.definition_mapper:
            error.error(f"Redefinition of label '{name}' in scope '{routine}'")
        self.definition_mapper[key] = self.address()

    def define_routine(self, name):
        if name in self.routine_mapper:
            error.error(f"Redefinition routine '{name}'")
        self.routine_mapper[name] = self.address()

    def lookup_local_label(self, name, routine):
        key = (name, routine)
        if key not in self.definition_mapper:
            error.error(f"Label '{name}' not defined in scope '{routine}'")
        return self.definition_mapper[key]

    def lookup_routine(self, name):
        if name not in self.routine_mapper:
            error.error(f"Routine '{name}' not defined")
        return self.routine_mapper[name]

    def check_routine_defined(self, name):
        return name in self.routine_mapper

    def address(self):
        return self.addr + self.link_header_size

    def render(self):
        return "\n".join(map(str, self.seq))

    def assemble(self, entry_origin):
        self.seq.insert(0, command('call', entry_origin))
        self.seq.insert(1, command('halt', None))

        return self.render()

