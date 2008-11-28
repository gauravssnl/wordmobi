#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Sintaxe: $0 version"
	exit 1
fi

APPNAME="wordmobi"
CAPBLS="NetworkServices+LocalServices+ReadUserData+WriteUserData"
SRCDIR="src"
TXTFILE="wordmobi_inst.txt"
TMPDIR="src.tmp"

PYFILES="viewcomments.py wmutil.py newpost.py settings.py persist.py editpost.py filesel.py viewpost.py wordmobi.py wordpresslib.py dt.py xmllib.py xmlrpclib.py"

if [ ! -d "$TMPDIR" ]
then
	mkdir "$TMPDIR"
fi

cd "$SRCDIR"
cp $PYFILES "../$TMPDIR"
cd ..
cp $TMPDIR/wordmobi.py $TMPDIR/default.py

python ./ensymble.py py2sis 	--uid=0xefefefef 	\
				--version="$1" 		\
				--appname="$APPNAME" 	\
				--textfile="$TXTFILE"	\
				--icon="$APPNAME.svg"	\
				--caps="$CAPBLS"	\
				"$TMPDIR" "$APPNAME-$1.sis"

