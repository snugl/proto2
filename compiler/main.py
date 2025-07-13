#!/usr/bin/python3
import sys

import lex
import tree
import emission


def compile(path):
    stream = lex.tokenize(path)
    root = tree.Node.parse(stream, root=True)

    output = emission.Buffer()
    root.infer()
    root.generate(output)

    output('mov', 'rax', 60)
    output('mov', 'rdi', 0)
    output('syscall')
    output.assemble('main')


    print(output.render())








def main():
    compile(sys.argv[1])

if __name__ == "__main__":
    main()
