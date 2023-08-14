Instructions
============

Summary
-------

A minimal set of virtual machine instructions is defined with the following
aims:

* Support small, specialised pieces of code, not general purpose programming.
* Use as little space as possible for commonly used programming patterns.
* Allow implementation on 8-bit microcomputers.

Instead of using a stack-based approach, or mapping closely to the semantics of
machine code of a specific CPU, like the 6502, the virtual machine uses a set
of instructions that operate on a collection of virtual registers.

There are 16 general purpose registers, each 8 bits wide. Pairs of registers
are used to refer to addresses that are 16 bits wide.

Format
------

Each instruction begins with a byte containing the type of instruction in the
lowest 4 bits. The top 4 bits contain either additional context or the first
operand.

Any additional operands are supplied in following bytes, with each register
operand using 4 bits.

Definitions
-----------

Register operands are indicated by R.

Constant values are indicated by C.

Addresses are indicated by A.

Offsets are indicated by O.

Values are indicated by V.

======  =======     ========    ==========  ======= ======= ======================================
Name    Operands (each 4 bits in size)                      Note
======  =================================================== ======================================
lc      R(dest)     V(low)      V(high)                     Load constant
cpy     R(dest)     R(src)      V(shift)                    Copy with optional shift
add     R(dest)     R(first)    R(second)
sub     R(dest)     R(first)    R(second)
and     R(dest)     R(first)    R(second)
or      R(dest)     R(first)    R(second)
xor     R(dest)     R(first)    R(second)
not     R(dest)     R(src)
ld      R(dest)     R(low)      R(high)
st      R(dest)     R(low)      R(high)
b*      cond        R(first)    R(second)   O(low)  O(high) cond described below
b       O(low)      O(high)                                 Unconditional branch
js                  A(0)        A(1)        A(2)    A(3)
jsi     R(base)                                             Using address in R(base) and R(base+1)
ret
======  =======     ========    ==========  ======= ======= ======================================

The *cond* operand enables conditional execution for branch instructions.
Each of the lowest 3 bits are used to indicate that the instruction should be
executed if the corresponding condition is met. These map easily to processor
flags.

======  ==============  ===============================
Bit     Meaning         Equivalent 6502 processor flags
======  ==============  ===============================
0       Less than       N
1       Equals          Z
2       Greater than    C & !Z
======  ==============  ===============================

So a *cond* value of 1 indicates that an instruction should only be executed
if the value held by *R(first)* is less than that held by *R(second)*.

A *cond* value of 6 indicates that an instruction should only be executed
if the value held by *R(first)* is greater than or equal to that held by
*R(second)*.

Unconditional branches are encoded with a *cond* value of 7.

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
