"""
pretty.py - Pretty printing functions and data.

Copyright (C) 2021 David Boddie <david@boddie.org.uk>

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

bold = "\x1b[1m"
end = "\x1b[m"
comment_code = "\x1b[92m"

def rgb(r, g, b):
    return "\x1b[38;2;%i;%i;%im" % (r, g, b)

def bgnd_rgb(r, g, b):
    return "\x1b[48;2;%i;%i;%im" % (r, g, b)

def Int(c):
    return bold + rgb(255,125,0) + str(c) + end

def Str(c):
    return rgb(0,160,255) + repr(c) + end

def Bool(c):
    return rgb(255,255,0) + str(c) + end

def Ins(c):
    return rgb(240,240,240) + c + end

def Label(c):
    return bold + c + end
