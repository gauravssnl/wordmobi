#!/bin/bash

VER="0.2"
APPNAME="sigwatch"
CAPBLS="ReadUserData+WriteUserData"

python ./ensymble.py py2sis 	--uid=0xefefefe9 	\
				--version="$VER"	\
				--appname="$APPNAME" 	\
				--caps="$CAPBLS"	\
				"$APPNAME.py" 		\
				"$APPNAME.sis"

