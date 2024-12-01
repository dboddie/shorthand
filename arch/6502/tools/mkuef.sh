#!/bin/bash

set -e

if [[ $# != 2 ]]; then
    echo "usage: mkuef.py <6502 code file> <UEF file>"
    exit 1
fi

echo -n '$.'`basename "$1"`' E02 E02 ' > "$1".inf
printf "%x\n" `stat --printf="%s" $1` >> "$1".inf

UEFtrans.py "$2" new Electron 0
UEFtrans.py "$2" append "$1"
