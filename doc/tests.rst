Tests
=====

The ``tests`` directory contains two subdirectories: ``data`` and ``programs``.

The ``programs`` subdirectory contains source programs for the `assembler`_.
Ideally, these programs would be assembled, run in the `simulator`_, then
their output state compared to the expected value.

The ``data`` subdirectory contains input and output data for the tests.

An example test
---------------

The ``tests/programs/decompress.txt`` file contains a program to decompress a
compressed text string. This program can be assembled from the root directory
of the repository in the following way:

.. code:: bash

    ./tools/assembler.py tests/programs/decompress.txt /tmp/asm.out

Before the test can be run in the simulator, test data for the program needs
to be created from the original ``tests/data/sample.txt`` text file.
This is compressed using the ``tools/compression/distance_pair.py`` tool:

.. code:: bash

    ./tools/compression/compress.py --compress --bits 4 tests/data/sample.txt tests/data/compressed.bin

The program expects to find compressed data at a particular address in the
simulator's memory. We specify this by passing the ``-d`` option to
``tools/simulator.py`` with two arguments: the address and the name of file to
unpack at that address. The program writes the decompressed output text to
memory, starting at another fixed address. We collect this data by passing
the ``-x`` option and two arguments: the start address of the output data and
the number of bytes to read:

.. code:: bash

    ./tools/simulator.py -d 8192 tests/data/compressed.bin -x 12288 164 /tmp/asm.out

The result is a dump of the memory from the simulator after the program has
finished running. It should contain a copy of the original uncompressed text
string.

.. _`assembler`: assembler.rst
.. _`simulator`: simulator.rst
