@echo off

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TXTFILE=README
SET TMPDIR=src.tmp
SET ICON=wordmobi.svg

IF NOT EXIST %TMPDIR% mkdir %TMPDIR%

copy  %SRCDIR%\*.py  %TMPDIR%

copy %SRCDIR%\wordmobi.py %TMPDIR%\default.py

%PYTHON% ensymble.py py2sis --verbose --uid=0xefefefef --version="%1" --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%ICON%" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%1.sis"

goto end

:error
echo Sintaxe: %0 version

:end
