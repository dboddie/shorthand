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
(typically adjacent) are used to refer to addresses that are 16 bits wide.
Registers are implemented as bytes in a block of memory that can hold a larger
number of registers than a default set of 16. By treating registers as elements
in a byte array whose base in the larger memory block can be shifted, windows
of registers can be used for different purposes.

Subroutines
-----------

Local registers in subroutines are supported by adjusting the base address used
to access registers. This could be implemented in two ways: by adjusting the
base address to a higher value, or by adjusting it a lower value.

Adjusting the base higher would prevent a subroutine from accessing its
caller's registers, and it would allow the calling routine to fine-tune use
of registers at different points in its execution. However, the size of the
adjustment would need to be recorded so that it could be obtained at run-time
and undone when the subroutine returns.

Adjusting the base lower would require the subroutine to declare the number of
registers it needs, but it would make the task of undoing the adjustment easier
since it would always be the same for any call to the subroutine.

Since it is easier and more consistent to let the subroutine's requirements
determine the size of the adjustment, and since a positive adjustment requires
the calling routine's requirements to be taken into account, a negative
adjustment is used.

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

Addresses are indicated by A.

Offsets are indicated by O.

Integer values are indicated by V, and are 4 bits in size.

======  ======  ==========  ==========  ==========  ==========  ==========  =========================
Number  Name    Operands (each 4 bits in size)                              Note
======  ======  ==========================================================  =========================
0       lc      R(dest)     V(low)      V(high)                             Load constant
1       cpy     R(dest)     R(src)      V(shift)                            Copy with optional shift
2       add     R(dest)     R(first)    R(second)                           Can set carry
3       sub     R(dest)     R(first)    R(second)                           Can set carry
4       and     R(dest)     R(first)    R(second)
5       or      R(dest)     R(first)    R(second)
6       xor     R(dest)     R(first)    R(second)
7       ld      R(dest)     R(low)      R(high)
8       st      R(src)      R(low)      R(high)
9       b*      cond        O(low)      O(high)     R(first)    R(second)   cond described below
9       b       cond=7      O(low)      O(high)                             Unconditional branch
9       not     cond=0      R(dest)     R(src)
10      adc     R(dest)                                                     Increment if carry set
11      sbc     R(dest)                                                     Decrement if carry set
12      js      V(args)     A(0)        A(1)        A(2)        A(3)
13      jss     V(args)     O(low)      O(high)
14      ret     V(args)
15      sys     V(value)
======  ======  ==========  ==========  ==========  ==========  ==========  =========================

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

The ``cpy`` instruction encodes the extent of a right shift operation on the
value held in the source register. Left shifts are expressed as negative shift
values using the top bit of the operand as a sign bit. The allowed range of
shifts is -7 to 7 inclusive. Since -8 (0x8) is not used, the encoding for
``cpy R(dest) R(src) -8`` could be used for another instruction.

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
