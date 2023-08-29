Assembler
=========

The assembler reads input files containing assembly language statements,
checks them for validity, and writes an encoded sequence of instructions to a
file.

Running the assembler
---------------------

The assembler has the following command line usage:

::

    usage: ./tools/assembler.py [-c] [-v] [-b <base address>] <input file> <output file>

The assembler reads the given ``<input file>`` and writes encoded output to
the ``<output file>`` specified.

The ``-v`` option enables verbose output, printing information to standard
output as the assembler processes, and the ``-c`` option enables colouring of
this output to help with legibility.

By default, the instructions are assembled to run at an address of zero. This
can be changed by passing the ``-b`` option and specifying a base address.

Assembly language syntax and usage
----------------------------------

The assembler only supports a very simple, line-based syntax, with one
statement on each line.

Statements are whitespace-separated sequences of tokens, beginning with an
instruction name and followed by a sequence of operands:

::

    <instruction> <operand>...

For example, an ``add`` instruction might look like this:

::

    add r0 r1 r2

Registers can be written as decimal integer values, either with an ``r`` prefix
or without. They are reduced to integer values before encoding. The following
instruction is equivalent to the previous one:

::

    add r0 1 2

Aliases can be defined to make code more understandable. For example, this
definition allows ``offset`` to be used in place of ``r1``:

::

    offset=r1
    add r0 offset r2

Aliases can be redefined, so that only instructions that follow the
redefinition will use the redefined value.

Integer values can be written as decimal or hexadecimal numbers:

::

    lc four 4
    lc mask 0x0f

Comments begin at a semicolon (``;``) or hash (``#``) character and end at the
end of the same line.

::

    # Count from 0 to 10
    lc r0 0     ; start
    lc r1 1     ; increment
    lc r2 10    ; finish

Labels are defined with a trailing colon (``:``) character, and can be used in
instructions that encode branches or jumps:

::

    loop:
        add r0 r0 r1
        bne r0 r2 loop

Subroutines are defined in the same way as labels, but they also include a
value that specifies the number of new registers that the subroutine uses:

::

    two_locals: 2
        lc r0 255
        lc r1 254
        ret

    main:
        lc r0 123
        js two_locals

In this case, the ``two_locals`` subroutine reserves two new registers for the
two local registers that it uses. See the `js`_ and `ret`_ instructions for
more information about how registers are handled in cases like these.

The instruction set places constraints on register numbers, integer values,
branch offsets and the offsets used for short jumps to subroutines.
The assembler will report an error if the input falls outside these
constraints.

Summary of instructions
-----------------------

Although the `instructions`_ document describes the design and encoding of
instructions, it is more useful at this point to give the assembly language
syntax and meaning of each of the instructions.

Note that operands are mostly registers, with constant integer values only
being used in the `lc`_ instruction. Although the targets of branch and jump
instructions are encoded as integer offsets and addresses, the assembler only
accepts labels when generating these instructions.

lc
~~

Syntax:

::

    lc <register> <value>

Loads the constant 8-bit value into the specified register.

cpy
~~~

Syntax:

::

    cpy <dest> <src> <shift>

Copies the contents of the source register into the destination register with
an optional shift. Positive shift values represent right shifts; negative shift
values represent left shifts.

add
~~~

Syntax:

::

    add <dest> <first> <second>

Adds the contents of the first register to the contents of the second register
and stores the result in the destination register.

Sets the carry flag if the result exceeds 255. In this case the value stored
in the destination register is the lowest 8 bits of the result.

adc
~~~

Syntax:

::

    adc <dest>

Increments the contents of the destination register if the carry flag is set.

This instruction will clear the carry flag unless the updated value of the
destination register exceeds 255. In such a case, the destination register will
contain zero and the carry flag will be set.

sub
~~~

Syntax:

::

    sub <dest> <first> <second>

Subtracts the contents of the second register from the contents of the first
register and stores the result in the destination register.

Sets the carry flag if the result exceeds 255. In this case the value stored
in the destination register is the lowest 8 bits of the result.

sbc
~~~

Syntax:

::

    sbc <dest>

Decrements the contents of the destination register if the carry flag is set.

This instruction will clear the carry flag unless the updated value of the
destination register falls below 0. In such a case, the destination register
will contain 255 and the carry flag will be set.

and
~~~

Syntax:

::

    and <dest> <first> <second>

Reads the contents of the first and second registers, performs a bitwise AND
operation on the two operands, and stores the result in the destination
register.

or
~~~

Syntax:

::

    or <dest> <first> <second>

Reads the contents of the first and second registers, performs a bitwise OR
operation on the two operands, and stores the result in the destination
register.

xor
~~~

Syntax:

::

    xor <dest> <first> <second>

Reads the contents of the first and second registers, performs a bitwise XOR
operation on the two operands, and stores the result in the destination
register.

not
~~~

Syntax:

::

    not <dest> <src>

Reads the contents of the source register, performs a bitwise NOT operation on
the value, and stores the result in the destination register.

ld
~~~

Syntax:

::

    ld <dest> <low> <high>

Reads the contents of the low and high registers as the low and high bytes in
a 16-bit address, reads the contents of that address, and stores the result in
the destination register.

st
~~~

Syntax:

::

    st <src> <low> <high>

Reads the contents of the low and high registers as the low and high bytes in
a 16-bit address, and stores the contents of the source register at that
address.

b
~

Syntax:

::

    b <label>

Unconditionally branches to the specified label.

beq
~~~

Syntax:

::

    beq <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the values are equal (first == second).

bge
~~~

Syntax:

::

    bge <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the first value is greater than or equal to the second value
(first >= second).

bgt
~~~

Syntax:

::

    bgt <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the first value is greater than the second value (first > second).

ble
~~~

Syntax:

::

    ble <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the first value is less than or equal to the second value
(first <= second).

blt
~~~

Syntax:

::

    blt <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the first value is less than the second value (first < second).

bne
~~~

Syntax:

::

    bne <first> <second> <label>

Compares the contents of the first and second registers, branching to the given
label if the values are not equal (first == second).

js
~~

Syntax:

::

    js <label>

Jumps to the specified subroutine, storing the return address on the return
stack, and decreases the register base address by the amount associated with
the subroutine.

This instruction updates the register base address to provide space for a local
scope. Consider the case just before a jump to a subroutine with 2 local
registers:

=========== === === === === === ===
*Registers* r0  r1  r2  r3  r4  ...
----------- --- --- --- --- --- ---
*Values*    123 32  0   1   7   ...
=========== === === === === === ===

After the jump, the registers visible to the code now look like this, with the
calling routine's registers also shown for comparison:

============ === === === === === === === ===
*Caller*             r0  r1  r2  r3  r4  ...
------------ --- --- --- --- --- --- --- ---
*Values*     ... ... 123 32  0   1   7   ...
------------ --- --- --- --- --- --- --- ---
*Subroutine* r0  r1  r2  r3  r4  r5  r6  ...
============ === === === === === === === ===

This is because the registers for each routine are referenced relative to a
base address:

============ === === === === === === === ===
*Memory*     ... ... 123 32  0   1   7   ...
------------ --- --- --- --- --- --- --- ---
*Caller*     ... ... ^
------------ --- --- --- --- --- --- --- ---
*Subroutine* ^
============ === === === === === === === ===

jss
~~~

Syntax:

::

    jss <label>

A variant of `js`_ that encodes to a smaller instruction but which is limited
to jumps between -128 and 127 bytes inclusive.

ret
~~~

Syntax:

::

    ret

Returns from the current subroutine, popping the return address from the return
stack and increasing the register base address by the amount associated with
the current subroutine.

When a subroutine returns, the number of local registers encoded into the
instruction is used by the instruction to adjust the register base address
back to the value it had before the call.

Consider the case in the `jss`_ instruction where a call is made to a
subroutine with 2 local registers. When the subroutine returns, the base
address is increased by two bytes:

============ === === === === === === === ===
*Subroutine* r0  r1  r2  r3  r4  r5  r6  ...
------------ --- --- --- --- --- --- --- ---
*Values*     ... ... 123 32  0   1   7   ...
------------ --- --- --- --- --- --- --- ---
*Caller*             r0  r1  r2  r3  r4  ...
============ === === === === === === === ===

As a result, the values stored in the *subroutine's* ``r0`` and ``r1``
registers are no longer accessible, and the virtual machine can only access the
registers starting from the *caller's* ``r0``.

sys
~~~

Syntax:

::

    sys <number>

Calls the system routine identified by the given number.


.. _`instructions`: instructions.rst
