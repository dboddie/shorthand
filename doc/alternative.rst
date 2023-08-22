Alternative Instructions
========================

Summary
-------

Similar to the regular instructions except using an accumulator to hold
intermediate results.

As before, there are 16 general purpose registers, each 8 bits wide. Pairs of
registers are used to refer to addresses that are 16 bits wide. Registers are
implemented as bytes in a block of memory that can hold a larger number of
registers than a default set of 16. By treating registers as elements in a byte
array whose base in the larger memory block can be shifted, windows of
registers can be used for different purposes.

Definitions
-----------

======  ==========  ======= ======= ======= ======= =========================================
Name    Operands (each 4 bits in size)              Note
======  =========================================== =========================================
lc      R(dest)     V(lo)   V(hi)                   Load constant (sets A)
cpy     R(dest)     R(src)  V(sh)                   Copy with optional shift (sets A)
cmp     R(op1)      R(op2)                          Compare R(op1) with R(op2)
lr      R(src)                                      Load R(src) into A
sr      R(dest)                                     Store A into R(dest)
add     R(other)                                    (sets A)
sub     R(other)                                    (sets A)
and     R(other)                                    (sets A)
or      R(other)                                    (sets A)
xor     R(other)                                    (sets A)
ld      R(low)                                      Load from address R(lo) | (R(hi) << 8) (sets A)
st      R(low)                                      Stores A to address R(hi)R(lo)
b*      cond        O(lo)   O(hi)                   cond described below
b       cond=15     O(lo)   O(hi)                   Unconditional branch
adc     R(other)                                    Increment if carry set
sbc     R(other)                                    Decrement if carry set
js      V(args)     A(0)    A(1)    A(2)    A(3)
ret     V(args)
======  ==========  ======= ======= ======= ======= =========================================

The `lr` and `sr` instructions are encoded 

The `not` instruction is missing because there is no space for it. It can be
expressed with an `xor` instruction with an operand of `0xff`. Alternatively,
the `cpy` instruction could be modified to treat the special case where the
shift is -8 as a `not` instruction, using one more byte than before. However,
the `cmp` instruction currently uses that encoding.

The `cmp` instruction is needed because the `sub` instruction, which could
otherwise be used for comparisons, modifies the accumulator. It is encoded
using the `cpy R(dest) R(src) -8` instruction.

The `sys` instruction is also missing because there is no space for it.
However, a check could be added to the `js` instruction for specific addresses.

Patterns
--------

Add two values:

==========  =============================== ==========
Processor   Instructions                    Size
==========  =============================== ==========
6502        Load constant, add, store value 2 + 2 + 2
VM          Load constant, add, store value 2 + 1 + 2
6502        Load value, add, store value    2 + 2 + 2
VM          Load value, add, store value    2 + 1 + 2
==========  =============================== ==========

If statement:

=========   ==============================  ==========
Processor   Instructions                    Size
=========   ==============================  ==========
6502        Load value, compare, branch     2 + 2 + 2
VM          Load value, compare, branch     2 + 1 + 2
=========   ==============================  ==========
