#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Sintaxe: $0 version"
	exit 1
fi

APPNAME="wordmobi"
CAPBLS="NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment"
SRCDIR="src"
TXTFILE="README"
TMPDIR="src.tmp"
ICON="wordmobi.svg"

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
				--icon="$ICON"	\
				--caps="$CAPBLS"	\
				"$TMPDIR" "$APPNAME-$1.sis"

