#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Sintaxe: $0 version"
	exit 1
fi

APPNAME="wordmobi"
CAPBLS="NetworkServices+LocalServices+ReadUserData+WriteUserData"
SRCDIR="src"
TXTFILE="README"
TMPDIR="src.tmp"

if [ ! -d $TMPDIR ]
then
	mkdir $TMPDIR
fi

cp  $SRCDIR/*.py $TMPDIR/

cp $TMPDIR/wordmobi.py $TMPDIR/default.py

python ./ensymble.py py2sis 	--uid=0xefefefef 	\
				--version="$1" 		\
				--appname="$APPNAME" 	\
				--textfile="$TXTFILE"	\
				--icon="$APPNAME.svg"	\
				--caps="$CAPBLS"	\
				"$TMPDIR" "$APPNAME-$1.sis"

