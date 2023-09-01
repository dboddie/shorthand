Background and motivations
==========================

Introduction
------------

The motivation behind defining a set of virtual `instructions`_ came from
thinking about how to save memory when writing non-speed-critical code for the
6502 CPU.
Even in programs where a lot of the code needs to run quickly, and which is
often also heavily optimised for space, there are routines that don't need to
run quickly and which take up space that could be used for optimised routines
that need space for their approaches. Things like look-up tables or room for
caching cannot be used due to the lack of memory.

These days, the need for optimisations is tied into games programming, where
there is a requirement to have routines for things like printing high score
tables, initialising the screen or resetting the game. Some of these routines
could run quite slowly compared to gameplay routines, and the user would not
notice.

In my own code, I tend to think of address ranges when writing routines, and
write fairly simple routines with perhaps only 8 or 16 bytes to hold variables.
It occurred to me that even 6502 instructions operating on zero page addresses
are inefficient if one only needs to operate on 16 variables at most.
For example, an instruction to load a byte from a zero page address could be
optimised for space:

::

    lda #$84        ; 1 byte for lda, 1 byte for #$80
    ld 4            ; 1 byte = 4 bits for ld, 4 bits for 4

In this case, the variables would be stored from addresses $80 to $8f.
Applying this constraint on the number of variables in use, one could simplify
many of the other 6502 instructions in a similar way.

Existing work
-------------

The most recognisable existing work is the `SWEET16`_ instruction set that was
designed for use with the Apple II computer which also used a 6502 CPU.

Patterns
--------

Add two values:

=========   ==============================  ==========
Processor   Instructions                    Size
=========   ==============================  ==========
6502        Load value, add, store value    2 + 2 + 2
VM          Add                             2
=========   ==============================  ==========

If statement:

=========   ==============================  ==========
Processor   Instructions                    Size
=========   ==============================  ==========
6502        Load value, compare, branch     2 + 2 + 2
VM          Branch                          3
=========   ==============================  ==========

.. _`instructions`: instructions.rst
.. _`SWEET16`: https://en.wikipedia.org/wiki/SWEET16