#!/bin/bash

VER="0.1"
APPNAME="remoteshell"
CAPBLS="NetworkServices+LocalServices+ReadUserData+WriteUserData"

python ./ensymble.py py2sis 	--uid=0xefefefee 	\
				--version="$VER"	\
				--appname="$APPNAME" 	\
				--caps="$CAPBLS"	\
				"$APPNAME.py" 		\
				"$APPNAME.sis"

