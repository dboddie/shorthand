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

======= ======  ==========  ======= ======= ======= ======= =========================================
Number  Name    Operands (each 4 bits in size)              Note
======= ======  =========================================== =========================================
0       lc      R(dest)     V(lo)   V(hi)                   Load constant (sets A)
------- ------  ----------  ------- ------- ------- ------- -----------------------------------------
1       cpy     R(dest)     R(src)  V(sh)                   Copy with optional shift (sets A)
1       cmp     R(op1)      R(op2)  V(sh)=8                 Compare A with R(op1)
------- ------  ----------  ------- ------- ------- ------- -----------------------------------------
2       lr      R(src)                                      Load R(src) into A
3       sr      R(dest)                                     Store A into R(dest)
4       add     R(other)                                    (sets A)
5       sub     R(other)                                    (sets A)
6       and     R(other)                                    (sets A)
7       or      R(other)                                    (sets A)
8       xor     R(other)                                    (sets A)
9       ld      R(low)                                      Load from address R(lo) | (R(hi) << 8) (sets A)
10      st      R(low)                                      Stores A to address R(hi)R(lo)
------- ------  ----------  ------- ------- ------- ------- -----------------------------------------
11      b*      cond        O(lo)   O(hi)                   cond described below
11      b       cond=15     O(lo)   O(hi)                   Unconditional branch
11      sys     V(value)    0       0
------- ------  ----------  ------- ------- ------- ------- -----------------------------------------
12      adc     R(other)                                    Increment if carry set
13      sbc     R(other)                                    Decrement if carry set
14      js      V(args)     A(0)    A(1)    A(2)    A(3)
15      ret     V(args)
======= ======  ==========  ======= ======= ======= ======= =========================================

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
However, a check could be added to the `js` instruction for specific addresses,
or a special case in the `b*` instructions could be used where offset of zero
is interpreted as `sys` call, and the *cond* field interpreted as a call
number.

Patterns
--------

Add two values:

==========  =============================== ==========
Processor   Instructions                    Size
==========  =============================== ==========
6502        Load constant, add, store value 2 + 2 + 2
VM          Load constant, add, store value 2 + 1 + 2
6502        Load zp, add, store zp          2 + 2 + 2
VM          Load reg, add, store reg        1 + 1 + 1
==========  =============================== ==========

If statement:

=========   ==============================  ==========
Processor   Instructions                    Size
=========   ==============================  ==========
6502        Load zp, compare, zp            2 + 2 + 2
VM          Load reg, compare, branch       1 + 2 + 2
=========   ==============================  ==========
