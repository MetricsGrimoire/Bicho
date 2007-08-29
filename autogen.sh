#!/bin/sh

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="Bicho"

(test -f $srcdir/configure.in \
    && test -f $srcdir/README \
) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

. $srcdir/common/bicho-autogen.sh
