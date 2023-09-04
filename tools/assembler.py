#!/usr/bin/env python3
# -*- coding: latin1 -*-

"""
assembler.py - An assembler for a virtual instruction set.

Copyright (C) 2023 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from common import get_int, opt
import pretty
import struct, sys

def error(msg, l):
    sys.stderr.write(msg + " on line %i\n" % l)
    sys.exit(1)

def usage(args):
    sys.stderr.write("usage: %s [-c] [-v] [-b <base address>] <input file> <output file>\n" % sys.argv[0])
    sys.exit(1)

def remove_comments(line):

    for c in "#;":
        at = line.find(c)
        if at != -1: line = line[:at]
        line = line.strip()

    return line

def split_pair(line, c, l):
    pieces = line.split(c)
    if len(pieces) != 2:
        error("invalid definition", l)
    left, right = pieces
    return left.strip(), right.strip()

def define_label(label, value):

    value, nparams = split_pair(value, ",", l)
    np = get_int(nparams)
    labels[label] = (get_int(value), np, True)

labels = {}
registers = {}

def process(lines, out_f, verbose):

    current_label = ""

    for scan in 0, 1:
        l = 1
        addr = base_addr
        for line in lines:
            line = remove_comments(line)

            if ":" in line:
                # Record labels and any numbers of registers for subroutines
                label, nparams = split_pair(line, ":", l)
                np = get_int(nparams)
                if scan == 0:
                    # Record the non-absolute address and the number of parameters.
                    labels[label] = (addr, np, False)
                else:
                    if verbose:
                        if nparams:
                            print(Label(label + ":") + " %i" % np)
                        else:
                            print(Label(label + ":"))
                    if nparams:
                        current_label = label
                l += 1
                continue
            elif "=" in line:
                # Allow label and register assignments
                label, value = split_pair(line, "=", l)
                if "," in value:
                    define_label(label, value)
                else:
                    if value.lower().startswith("r"):
                        registers[label] = value
                    else:
                        labels[label] = (get_int(value), 0, True)

                l += 1
                continue

            pieces = line.split()
            name, args = pieces[:1], pieces[1:]
            if not name:
                l += 1
                continue
            else:
                name = name[0]

            try:
                n, fmt, size, inst = instructions[name]
            except KeyError:
                error("unknown instruction '%s'" % name, l)

            if scan == 0:
                addr += size
            else:
                addr += inst(n, fmt, l, name, args, addr, current_label, out_f, verbose)
            l += 1

def check_args(args, fmt, l):

    opt = 0
    for p in fmt:
        if p.endswith("?"): opt += 1

    if not (len(fmt) - opt) <= len(args) <= len(fmt):
        error("invalid number of arguments", l)

    values = []

    for a, p in zip(args, fmt):
        p.rstrip("?")
        if p[0] == "R":
            # Registers are specified as decimals with an optional leading R or r.
            a = a.lstrip("Rr")
            if a in registers:
                a = registers[a].lstrip("Rr")
        elif p[0] == "S" or p[0] == "H":
            # Shifts are specified as decimals.
            pass
        elif p[0] == "B" or p[0] == "A":
            # Byte and address values can be specified in hexadecimal with a
            # leading 0x.
            a = a.lower()
        elif p[0] == "L":
            continue

        lower, upper = value_limits[p[0]]

        try:
            v = get_int(a)
            if not lower <= v < upper: raise ValueError
            # Convert negative numbers to appropriate positive numbers.
            if v < 0: v += upper
        except ValueError:
            error("argument for %s (%s) not a valid value" % (p, repr(a)), l)

        values.append(v)

    return values

def inst_lc(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n | (values[0] << 4), values[1]))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_cpy(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    if len(values) < 3: values.append(0)

    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_3r(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_ldst(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    if len(values) < 3:
        r = values[1] + 1
        if r > 15: error("cannot assign implicit high address register", l)
        values.append(r)

    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_2r(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n, values[0] | (values[1] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_1r(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<B", n | (values[0] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 1

def inst_ret(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    if current_label not in labels:
        error("not in a subroutine", l)
    target, nparams, absolute = labels[current_label]

    out_f.write(struct.pack("<B", n | (nparams << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), nparams, args, values)
    return 1

def inst_bx(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)

    cond = cond_values[name.lower()]
    # Obtain the target address, discarding the number of parameters for
    # regular labels.
    target, nparams, absolute = labels[args[2]]
    offset = target - addr
    if not -128 <= offset < 128: error("branch offset out of range", l)

    if verbose: print(Int(addr) + ":", Ins(name), args, values, offset)

    if offset < 0: offset += 256
    out_f.write(struct.pack("<BBB", n | (cond << 4), offset,
                            values[0] | (values[1] << 4)))
    return 3

def inst_b(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    # Use a special value for unconditional branches.
    cond = 7

    # Obtain the target address, discarding the number of parameters for
    # regular labels.
    target, nparams, absolute = labels[args[0]]
    offset = target - addr
    if not -128 <= offset < 128: error("branch offset out of range", l)

    if verbose: print(Int(addr) + ":", Ins(name), args, values, offset)

    if offset < 0: offset += 256
    out_f.write(struct.pack("<BB", n | (cond << 4), offset))
    return 2

def inst_js(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    # Resolve the label to an index in the instruction output and add it to the
    # base address.
    target, nparams, absolute = labels[args[0]]
    values.append(target)

    if verbose: print(Int(addr) + ":", Ins(name), nparams, args, values)

    out_f.write(struct.pack("<BBB", n | (nparams << 4), values[0] & 0xff, values[0] >> 8))
    return 3

def inst_jss(n, fmt, l, name, args, addr, current_label, out_f, verbose):

    values = check_args(args, fmt, l)
    # Resolve the label to an index in the instruction output and add it to the
    # base address.
    target, nparams, absolute = labels[args[0]]
    offset = target - addr
    if offset < -128 or offset > 127: error("short jump out of range", l)
    values.append(offset)

    if verbose: print(Int(addr) + ":", Ins(name), nparams, args, values)

    out_f.write(struct.pack("<BB", n | (nparams << 4), values[0] & 0xff))
    return 2

value_limits = {
    "A": (0, 0x10000), "B": (-128, 256), "H": (0, 16), "R": (0, 16), "S": (-7, 16)
    }

cond_values = {
    "blt": 0b001,
    "beq": 0b010,
    "ble": 0b011,
    "bgt": 0b100,
    "bne": 0b101,
    "bge": 0b110
    }

instructions = {
    "lc": (0, ["Rdest", "Bvalue"], 2, inst_lc),
    "cpy": (1, ["Rdest", "Rsrc", "Sshift?"], 2, inst_cpy),
    "add": (2, ["Rdest", "Rfirst", "Rsecond"], 2, inst_3r),
    "sub": (3, ["Rdest", "Rfirst", "Rsecond"], 2, inst_3r),
    "and": (4, ["Rdest", "Rfirst", "Rsecond"], 2, inst_3r),
    "or": (5, ["Rdest", "Rfirst", "Rsecond"], 2, inst_3r),
    "xor": (6, ["Rdest", "Rfirst", "Rsecond"], 2, inst_3r),
    "ld": (7, ["Rdest", "Rlow", "Rhigh?"], 2, inst_ldst),
    "st": (8, ["Rsrc", "Rlow", "Rhigh?"], 2, inst_ldst),
    "beq": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bne": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "blt": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "ble": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bgt": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bge": (9, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    # Unconditional branch is encoded as a conditional branch with cond=15
    # but no registers.
    "b": (9, ["Llabel"], 2, inst_b),
    # Overload the branch instruction with cond=0 and no offset to encode a
    # not instruction.
    "not": (9, ["Rdest", "Rsrc"], 2, inst_2r),
    "adc": (10, ["Rdest"], 1, inst_1r),
    "sbc": (11, ["Rdest"], 1, inst_1r),
    "js": (12, ["Llabel"], 3, inst_js),
    "jss": (13, ["Llabel"], 2, inst_jss),
    "ret": (14, [], 1, inst_ret),
    "sys": (15, ["Hvalue"], 1, inst_1r)
    }

if __name__ == "__main__":

    args = sys.argv[:]
    verbose = opt(args, "-v")
    colour = opt(args, "-c")
    base, base_v = opt(args, "-b", 1, ["0"])
    base_addr = get_int(base_v)

    if colour:
        Ins, Int, Label, Str = pretty.Ins, pretty.Int, pretty.Label, pretty.Str
    else:
        Ins = Int = Label = Str = lambda x: str(x)

    if len(args) != 3:
        usage(args)

    lines = open(args[1]).readlines()
    out_f = open(args[2], "wb")

    process(lines, out_f, verbose)
    sys.exit()
