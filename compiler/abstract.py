
from dataclasses import dataclass
from dataclasses import field

@dataclass
class param_interface:
    in_param  : list[str] = field(default_factory=lambda: [])
    out_param : list[str] = field(default_factory=lambda: [])

    def add_in(self, iden):
        self.in_param.append(iden)

    def add_out(self, iden):
        self.out_param.append(iden)

    def render_space(self):
        return self.in_param + self.out_param

    def get_space_size(self):
        return len(self.render_space())

    def generate_variable_binding(self):
        params = self.render_space()
        offset = -(2 + len(params)) #offset from base pointer to start of pinterface

        binding = {}

        for index, name in enumerate(params):
            binding[name] = offset + index

        return binding



