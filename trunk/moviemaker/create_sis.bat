@echo off

SET VERSION=1.1.0
SET PYTHON=C:\Python25\python
SET APPNAME=MMaker
SET CAPBLS=LocalServices+NetworkServices+ReadUserData+WriteUserData+UserEnvironment


%PYTHON% .\ensymble.py py2sis --version="%VERSION%" --heapsize=4k,5M --appname="%APPNAME%" --caps="%CAPBLS%" mmaker.py "%APPNAME%%VERSION%.sis"

