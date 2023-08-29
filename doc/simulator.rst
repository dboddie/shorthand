Simulator
=========

Programs compiled to the instruction set can be run in the simulator. This
provides a simple virtual machine with a memory buffer that programs can be
loaded into and run. It also allows input data to be loaded into the
simulator's memory before running code, and can extract a region of the memory
for analysis outside of the simulator.

Running the simulator
---------------------

The simulator has the following command line usage:

::

    usage: ./tools/simulator.py [-c] [-v] [-b <base address>] [-d <data address> <data file>] [-x <address> <length>] [-s] <input file>

The simulator reads the given ``<input file>`` containing encoded instructions
produced by the assembler. It loads the file at the start of its memory buffer
(with an address of zero) unless the ``-b`` option is used to pass a base
address, in which case the file is loaded into the memory buffer at that
address.

It begins executing instructions from the start of the program in memory.
If the ``-s`` option is passed, the simulator will step through the
instructions, pausing for user input before each instruction is executed.

As with the assembler, the ``-v`` and ``-c`` options are used to obtain verbose
output with optional colouring.

The ``-d`` option can be used to specify the address in the simulator's memory
at which to load the contents of a file. This is done before the program is
executed. The ``-x`` option is used to specify the start and length of an area
of the simulator's memory to extract after the program has run. This allows the
output of a program to be analysed outside the simulator for testing purposes.
