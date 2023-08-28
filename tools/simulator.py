#!/usr/bin/env python3

from common import get_int, opt
import sys

# Reserve memory for variables and a return address stack.
stack = [0] * 128
rstack = [0] * 8
sp = len(stack) - 16
rsp = len(rstack) - 1
base_addr = 0
end = False
pc = 0
# Carry/borrow
cb = False
breakpoints = set()

def usage(args):
    sys.stderr.write("usage: %s [-c] [-v] [-b <base address>] "
                     "[-d <data address> <data file>] "
                     "[-x <address> <length>] [-s] "
                     "<input file>\n" % sys.argv[0])
    sys.exit(1)

def process():
    global pc

    pc = base_addr
    while not end:
        opcode = data[pc]
        inst = instructions[opcode & 0x0f]
        if single or verbose or pc in breakpoints:
            print(pc, inst)
            if single or pc in breakpoints:
                print(stack[sp:sp + 16])
                print(" ".join([("%02x" % x) for x in stack[sp:sp + 16]]))
                process_command(input(">"))
        inst(opcode)

    print(stack[sp:])

def process_command(t):
    global end, single

    single = True

    if extract:
        b = data[ex_addr:ex_addr + ex_length]
        if t == "x":
            i = 0
            while i < ex_length:
                for x in b[i:i + 16]:
                    print("%02x" % x, end=" ")
                i += 16
                print()
        elif t == "tx":
            print(bytes(b))
    elif t == "q": end = True
    elif t == "c": single = False
    elif t.startswith("b"):
        addr = t[1:].rstrip()
        if not addr:
            addr = pc
        else:
            addr = int(addr)
        breakpoints.add(addr)

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
    global cb, pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    v = stack[sp + first] + stack[sp + second]
    stack[sp + dest] = v & 0xff
    cb = v > 0xff
    pc += 2

def inst_sub(opcode):
    global cb, pc

    dest = opcode >> 4
    args = data[pc + 1]
    first, second = args & 0x0f, args >> 4
    v = stack[sp + first] - stack[sp + second]
    stack[sp + dest] = v & 0xff
    cb = v < 0
    pc += 2

def inst_adc(opcode):
    global cb, pc

    if cb:
        dest = opcode >> 4
        v = stack[sp + dest] + 1
        stack[sp + dest] = v & 0xff
        cb = v > 0xff
    pc += 1

def inst_sbc(opcode):
    global cb, pc

    if cb:
        dest = opcode >> 4
        v = stack[sp + dest] - 1
        stack[sp + dest] = v & 0xff
        cb = v < 0
    pc += 1

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

def inst_not():
    global pc

    args = data[pc + 1]
    dest, src = args & 0x0f, args >> 4
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
    data[addr] = stack[sp + src]
    pc += 2

def inst_bx(opcode):
    global pc

    cond = opcode >> 4
    offset = data[pc + 1]
    flags = 0
    if cond == 0:
        inst_not()
        return
    elif cond < 8:
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
    global pc, rsp, sp

    args = opcode >> 4
    low = data[pc + 1]
    high = data[pc + 2]
    rstack[rsp] = pc + 3
    rsp -= 1
    sp -= args
    pc = low | (high << 8)

def inst_jss(opcode):
    global pc, rsp, sp

    args = opcode >> 4
    offset = data[pc + 1]
    if offset >= 128: offset -= 256
    rstack[rsp] = pc + 2
    rsp -= 1
    sp -= args
    pc += offset

def inst_ret(opcode):
    global pc, rsp, sp

    args = opcode >> 4
    sp += args
    rsp += 1
    pc = rstack[rsp]

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
    inst_ld,        # R(dest)   R(low)      R(high)
    inst_st,        # R(src)    R(low)      R(high)
    inst_bx,        # cond      O(low)      O(high)     R(first)    R(second)
#   inst_not,       # R(dest)   R(src)
    inst_adc,       # R(dest)
    inst_sbc,       # R(dest)
    inst_js,        # V(args)   A(0)        A(1)        A(2)        A(3)
    inst_jss,       # V(args)   O(low)      O(high)
    inst_ret,       # V(args)
    inst_sys        # V(value)
    ]

if __name__ == "__main__":

    args = sys.argv[:]
    verbose = opt(args, "-v")
    colour = opt(args, "-c")
    base, base_v = opt(args, "-b", 1, "0")
    base_addr = get_int(base_v)
    single = opt(args, "-s")
    da, (data_addr, data_file) = opt(args, "-d", 2, ["0", ""])
    extract, (ex_addr, ex_length) = opt(args, "-x", 2, ["0", "0"])
    ex_addr = get_int(ex_addr)
    ex_length = get_int(ex_length)

    if len(args) != 2:
        usage(args)

    code = open(args[1], "rb").read()
    data = [0] * base_addr
    for c in code: data.append(c)
    # Append a sys 0 (exit) call.
    data.append(0x0f)
    data += [0] * (65536 - len(data))

    if da:
        data_addr = get_int(data_addr)
        for x in open(data_file, "rb").read():
            data[data_addr] = x
            data_addr += 1

    process()

    process_command("x")
    process_command("tx")

    sys.exit()
