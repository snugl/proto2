#!/usr/bin/python3

import sys
import tree
import emission
import error


entry_name = "main"

def compile(path):
    #lex, parse, expand imports
    root = tree.prepare(path)

    #output buffer
    output = emission.output()

    #actual compilation
    entry = root.get_routine(entry_name)
    entry.generate(output, root)

    #render ir
    entry_origin = output.lookup_routine(entry_name)
    build = output.assemble(entry_origin)
    
    with open('build', "w") as f:
        f.write(build)



def main():
    compile(sys.argv[1])


if __name__ == "__main__":
    main()
