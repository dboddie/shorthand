#!/usr/bin/env python3

from common import get_int, opt
import sys

# Reserve memory for variables.
stack = [0] * 128
sp = 112
base_addr = 0
end = False
pc = 0

def usage(args):
    sys.stderr.write("usage: %s [-c] [-v] <input file>\n" % sys.argv[0])
    sys.exit(1)

def process():
    global pc

    pc = base_addr
    while not end:
        opcode = data[pc]
        inst = instructions[opcode & 0x0f]
        if verbose: print(pc, inst)
        inst(opcode)

    print(stack[sp:])

def inst_lc(opcode):
    global pc

    dest = opcode >> 4
    value = data[pc + 1]
    stack[sp + dest] = value
    pc += 2

def inst_cpy(opcode):
    global pc

    dest = opcode >> 4
    src_shift = data[pc + 1]
    src, shift = src_shift & 0x0f, src_shift >> 4
    if shift >= 8:
        value = stack[sp + src] << (16 - shift)
    else:
        value = stack[sp + src] >> shift
    stack[sp + dest] = (value & 0xff)
    pc += 2

def inst_add(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    stack[sp + dest] = (stack[sp + first] + stack[sp + second]) & 0xff
    ### Handle carry
    pc += 2

def inst_sub(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    stack[sp + dest] = (stack[sp + first] - stack[sp + second]) & 0xff
    ### Handle borrow
    pc += 2

def inst_and(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    stack[sp + dest] = stack[sp + first] & stack[sp + second]
    pc += 2

def inst_or(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    stack[sp + dest] = stack[sp + first] | stack[sp + second]
    pc += 2

def inst_xor(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    stack[sp + dest] = stack[sp + first] ^ stack[sp + second]
    pc += 2

def inst_not(opcode):
    global pc

    dest = opcode >> 4
    src = data[pc + 1] & 0x0f
    stack[sp + dest] = ~stack[sp + src]
    pc += 2

def inst_ld(opcode):
    global pc

    dest = opcode >> 4
    args = data[pc + 1]
    low, high = args & 0x0f, args >> 4
    addr = stack[sp + low] | (stack[sp + high] << 8)
    stack[sp + dest] = data[addr]
    pc += 2

def inst_st(opcode):
    global pc

    src = opcode >> 4
    args = data[pc + 1]
    low, high = args & 0x0f, args >> 4
    addr = stack[sp + low] | (stack[sp + high] << 8)
    data[addr] = stack[sp + dest]
    pc += 2

def inst_bx(opcode):
    global pc

    cond = opcode >> 4
    offset = data[pc + 1]
    flags = 0
    if cond < 8:
        args = data[pc + 2]
        first, second = args & 0x0f, args >> 4
        if offset >= 128: offset -= 256
        v = stack[sp + first] - stack[sp + second]
        if v < 0: flags = 1
        elif v == 0: flags = 2
        elif v > 0: flags = 4

    if flags & cond != 0 or cond >= 8:
        pc += offset
    else:
        pc += 3

def inst_js(opcode):
    global pc, sp

    args = opcode >> 4
    low = data[pc + 1]
    high = data[pc + 2]
    sp -= 1
    stack[sp] = pc + 3
    sp -= args
    pc = low | (high << 8)

def inst_ret(opcode):
    global pc, sp

    args = opcode >> 4
    sp += args
    pc = stack[sp]
    sp += 1

def inst_sys(opcode):
    global end
    n = opcode >> 4
    if n == 0:
        end = True
    elif n == 15:
        print(stack[sp:])
    return 1

instructions = [
    inst_lc,        # R(dest)   V(low)      V(high)
    inst_cpy,       # R(dest)   R(src)      V(shift)
    inst_add,       # R(dest)   R(first)    R(second)
    inst_sub,       # R(dest)   R(first)    R(second)
    inst_and,       # R(dest)   R(first)    R(second)
    inst_or,        # R(dest)   R(first)    R(second)
    inst_xor,       # R(dest)   R(first)    R(second)
    inst_not,       # R(dest)   R(src)
    inst_ld,        # R(dest)   R(low)      R(high)
    inst_st,        # R(src)    R(low)      R(high)
    inst_bx,        # cond      O(low)      O(high)     R(first)    R(second)
    None,
    None,
    inst_js,        # V(args)   A(0)        A(1)        A(2)        A(3)
    inst_ret,       # V(args)
    inst_sys        # V(value)
    ]

if __name__ == "__main__":

    args = sys.argv[:]
    verbose = opt(args, "-v")
    colour = opt(args, "-c")
    base, base_v = opt(args, "-b", 1, "0")
    base_addr = get_int(base_v)

    if len(args) != 2:
        usage(args)

    code = open(args[1], "rb").read()
    data = [0] * base_addr
    for c in code: data.append(c)
    # Append a sys 0 (exit) call.
    data.append(0x0f)
    data += [0] * (65536 - len(data))
    process()
    sys.exit()
