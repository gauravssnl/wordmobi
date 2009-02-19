@echo off
REM
REM S60 5th Edition based on Symbian OS v9.4
REM

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TXTFILE=README
SET ICON=wordmobi.svg
SET TMPDIR=src.tmp

mkdir %TMPDIR%\extras\data\python
copy  %SRCDIR%\*.py  %TMPDIR%\extras\data\python
move %TMPDIR%\extras\data\python\default.py  %TMPDIR%\

%PYTHON% ensymble.py py2sis --verbose --heapsize=4k,5M --extrasdir=extras --uid=0xefefefef --version="%1" --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%ICON%" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%1-py191.sis"

goto end

:error
echo Sintaxe: %0 version

:end

