@echo off

SET VERSION=1.0.0
SET PYTHON=C:\Python25\python
SET CAPBLS=LocalServices+NetworkServices+ReadUserData+WriteUserData+UserEnvironment

SET APPNAME=TxFile
%PYTHON% .\ensymble.py py2sis --version="%VERSION%" --heapsize=4k,5M --appname="%APPNAME%" --caps="%CAPBLS%" txfile.py "%APPNAME%%VERSION%.sis"

SET APPNAME=RxFile
%PYTHON% .\ensymble.py py2sis --version="%VERSION%" --heapsize=4k,5M --appname="%APPNAME%" --caps="%CAPBLS%" rxfile.py "%APPNAME%%VERSION%.sis"

