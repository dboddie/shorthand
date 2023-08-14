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

import pretty
import struct, sys

def error(msg, l):
    sys.stderr.write(msg + " on line %i\n" % l)
    sys.exit(1)

def process(lines, out_f, verbose):

    labels = {}

    for scan in 0, 1:
        l = 1
        addr = 0
        for line in lines:
            # Remove comments
            at = line.find("#")
            if at != -1: line = line[:at]
            line = line.strip()

            # Register labels
            if line.endswith(":"):
                label = line.rstrip(":")
                if scan == 0:
                    labels[label] = addr
                elif verbose:
                    print(Label(label + ":"))
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
                addr += inst(n, fmt, l, name, args, addr, labels, out_f, verbose)
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
            a = a.lower().lstrip("r")
            base = 10
        elif p[0] == "S":
            # Shifts are specified as decimals.
            base = 10
        elif p[0] == "B" or p[0] == "A":
            # Byte and address values can be specified in hexadecimal with a
            # leading 0x.
            a = a.lower()
            if a.startswith("0x"):
                base = 16
            else:
                base = 10
        elif p[0] == "L":
            continue

        lower, upper = value_limits[p[0]]

        try:
            v = int(a, base)
            if not lower <= v < upper: raise ValueError
            # Convert negative numbers to appropriate positive numbers.
            if v < 0: v += upper
        except ValueError:
            error("argument for %s not a valid value" % p, l)

        values.append(v)

    return values

def inst_lc(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n | (values[0] << 4), values[1]))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_cpy(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    if len(values) < 3: values.append(0)

    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_3r(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_ldst(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    if len(values) < 3:
        r = values[1] + 1
        if r > 15: error("cannot assign implicit high address register", l)
        values.append(r)

    out_f.write(struct.pack("<BB", n | (values[0] << 4),
                            values[1] | (values[2] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_2r(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<BB", n, values[0] | (values[1] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 2

def inst_1r(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<B", n | (values[0] << 4)))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 1

def inst_0r(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    out_f.write(struct.pack("<B", n))
    if verbose: print(Int(addr) + ":", Ins(name), args, values)
    return 1

def inst_bx(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)

    cond = cond_values[name.lower()]
    offset = labels[args[2]] - addr

    if verbose: print(Int(addr) + ":", Ins(name), args, values, offset)

    if offset < 0: offset += 256
    out_f.write(struct.pack("<BBB", n | cond, values[0] | (values[1] << 4),
                            offset))
    return 3

def inst_b(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    offset = labels[args[0]] - addr

    if verbose: print(Int(addr) + ":", Ins(name), args, values, offset)

    if offset < 0: offset += 256
    out_f.write(struct.pack("<BB", n, offset))
    return 2

def inst_js(n, fmt, l, name, args, addr, labels, out_f, verbose):

    values = check_args(args, fmt, l)
    if name == "js": values.append(labels[args[0]])

    if verbose: print(Int(addr) + ":", Ins(name), args, values)

    out_f.write(struct.pack("<BBB", n, values[0] & 0xff, values[0] >> 8))
    return 3


value_limits = {
    "A": (0, 0x10000), "B": (-128, 256), "R": (0, 16), "S": (-7, 16)
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
    "not": (7, ["Rdest", "Rsrc"], 2, inst_2r),
    "ld": (8, ["Rdest", "Rlow", "Rhigh?"], 2, inst_ldst),
    "st": (9, ["Rsrc", "Rlow", "Rhigh?"], 2, inst_ldst),
    "beq": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bne": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "blt": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "ble": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bgt": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "bge": (10, ["Rfirst", "Rsecond", "Llabel"], 3, inst_bx),
    "b": (11, ["Llabel"], 2, inst_b),
    "js": (12, ["Llabel"], 3, inst_js),
    "jsa": (12, ["Aaddr"], 3, inst_js),
    "jsi": (13, ["Rbase"], 1, inst_1r),
    "ret": (14, [], 1, inst_0r),
    }

def opt(args, name):
    has_opt = name in args
    while name in args: args.remove(name)
    return has_opt

if __name__ == "__main__":

    args = sys.argv[:]
    verbose = opt(args, "-v")
    colour = opt(args, "-c")

    if colour:
        Ins, Int, Label, Str = pretty.Ins, pretty.Int, pretty.Label, pretty.Str
    else:
        Ins = Int = Label = Str = lambda x: x

    if len(args) != 3:
        sys.stderr.write("usage: %s [-v] <input file> <output file>\n" % sys.argv[0])
        sys.exit(1)

    lines = open(args[1]).readlines()
    out_f = open(args[2], "wb")

    process(lines, out_f, verbose)
    sys.exit()
