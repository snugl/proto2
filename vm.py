#!/usr/bin/python3

import sys





def lex(raw):
    prog = []
    for line_raw in raw.split('\n'):
        line = line_raw.strip().replace('  ', ' ')
        if not line: continue
        if line.startswith('"'): continue

        comps = line.split(' ', 1)
        inst = comps[0]
        arg  = comps[1] if len(comps) > 1 else None

        prog.append((inst, 
            int(arg) if arg and all(x.isdigit() or x in ('-') for x in arg) else arg
        ))

    return prog



def run(prog):

    mem_size = 65536
    heap_base = mem_size // 2


    pc = 0
    acc = 0
    mem = [0 for _ in range(mem_size)]
    stack = 0 #stack pointer
    base  = stack #base  pointer

    running = True


    def push(x):
        nonlocal mem, stack
        mem[stack] = x
        stack += 1

    def pull():
        nonlocal mem, stack
        stack -= 1
        return mem[stack]

    def block(content_size):
        nonlocal stack, acc
        real_size = content_size + 1

        push(real_size)
        acc = stack


    while pc < len(prog) and running:
        inst, arg = prog[pc]
        pc += 1


        #virtual arg, relative to stack frame
        varg = (base + arg) if type(arg) is int else None

        match inst:
            case 'const': acc = int(arg)

            #arithmatic
            case 'add':     acc += pull()
            case 'sub':     acc -= pull()
            case 'greater': acc = (acc > pull())
            case 'lesser' : acc = (acc < pull())
            case 'equal':   acc = (acc == pull())
            case 'mul':     acc = acc * pull()
            case 'inc':     acc += 1
            case 'dec':     acc -= 1
            case 'or':      acc |= pull()
            case 'and':     acc &= pull()

            #stack interface
            case 'push': push(acc)
            case 'pull': acc = pull()
            case 'dup' : push(mem[stack-1])

            #memory interface
            case 'load':  acc = mem[varg]
            case 'store': mem[varg] = acc

            #branching
            case 'jump':  pc = arg
            case 'branch':
                if acc != 0: pc = arg

            #routines
            case 'call':
                #flow control
                push(pc)
                pc = arg

                #frame control
                push(base) #save base pointer
                base = stack #construct new frame

            case 'return':
                stack = base  #collaps current frame (if it even exists)
                base = pull() #reconstruct old frame
                pc = pull()   #reconstruct old flow

            #memory manage
            case 'alloc': #allocate n spaces on stack
                stack += arg

            case 'free':  #free n spaces on stack
                stack -= arg

            #i know what you are OwO
            case 'trans': #alloc transient acc, base into acc
                size = acc
                block(size)
                stack += size

            #for deref/ref: acc is addr
            case 'deref': #acc = *acc
                acc = mem[acc]

            case 'ref': #*acc = pull()
                mem[acc] = pull()

            
            #heap
            case 'pers': #size of block by acc
                needed = acc + 1

                # *collars and leashes you* let's go for walkies~
                walker = heap_base

                trial = needed
                while trial > 0: #trial running
                    if mem[walker] == 0:
                        walker += 1
                        trial  -= 1
                    else:
                        walker += mem[walker] #skip block
                        trial = needed        #restart trial

                ptr = walker - needed
                mem[ptr] = needed #size header
                acc = ptr + 1

            
            case 'void': #free block by zero'ing
                start = acc - 1
                end   = start + mem[start]

                for addr in range(start, end):
                    mem[addr] = 0

            
            case 'write':
                print(chr(acc), end = '')
                
            case 'string':
                string = (arg
                    .strip("'")
                    .encode('utf-8')
                    .decode('unicode_escape') + '\0'
                )
                block(len(string))

                for char in string:
                    push(ord(char))


            #misc
            case 'debug': 
                match arg:
                    case 'expr':   print(acc)
                    case 'char':   print(chr(acc), end = '')
                    case 'value':  print(acc, end = '')
                    case 'string':
                        while mem[acc]:
                            print(chr(mem[acc]), end = '')
                            acc += 1
            case 'halt':  running = False


def main():
    
    with open(sys.argv[1], 'r') as f:
        prog = lex(f.read())

    run(prog)

if __name__ == '__main__':
    main()
