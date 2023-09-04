#!/usr/bin/env python3

"""
mkophis.py - Converts bytecode to Ophis assembler statements.

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

import sys

def usage(args):
    sys.stderr.write("usage: %s <bytecode file> <oph file>\n" % sys.argv[0])
    sys.exit(1)

def write_opcodes(f, opcodes):

    i = 0
    while i < len(opcodes):
        line = []
        for opcode in opcodes[i:i + 24]:
            line.append(opcode & 0xff)
        f.write(".byte " + ", ".join(map(str, line)) + "\n")
        i += 24

if __name__ == "__main__":

    args = sys.argv[:]

    if len(args) != 3:
        usage(args)

    f = open(args[1], "rb")
    g = open(args[2], "w")
    write_opcodes(g, f.read())

    sys.exit()
