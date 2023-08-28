# -*- coding: latin1 -*-

"""
common.py - Common routines for a suite of tools.

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

def get_int(s):
    if not s:
        return 0
    elif s.startswith("0x"):
        base = 16
    else:
        base = 10
    return int(s, base)

def opt(args, name, values=0, default=""):

    has_opt = name in args
    v = default[:]
    while name in args:
        at = args.index(name)
        v = args[at+1:at+1+values]
        args[:] = args[:at] + args[at+1+values:]

    if values == 0:
        return has_opt
    elif not v:
        usage(args)
    elif values > 1:
        return has_opt, v
    else:
        return has_opt, v[0]
