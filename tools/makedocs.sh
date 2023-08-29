#!/bin/sh

mkdir -p html
cp COPYING html/COPYING

for path in `find . -name "*.rst"`; do
    rel=`realpath --relative-to . $path`
    dn=`dirname $rel`

    if [ $dn != '.' ]; then
        mkdir -p html/$dn
    fi
    htmlname=`basename $rel .rst`
    rst2html --stylesheet doc/style/style.css $path > html/$dn/$htmlname.html
    sed -ri 's/\.rst"/\.html"/g' html/$dn/$htmlname.html
done
