#!/bin/bash

VERSION=1.1.0
PYTHON=/usr/bin/python2.5
APPNAME=MMaker
CAPBLS=LocalServices+NetworkServices+ReadUserData+WriteUserData+UserEnvironment


$PYTHON ./ensymble.py py2sis --version="$VERSION" --heapsize=4k,5M --appname="$APPNAME" --caps="$CAPBLS" mmaker.py "$APPNAME$VERSION.sis"

