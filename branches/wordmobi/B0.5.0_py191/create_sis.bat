@echo off

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TXTFILE=README
SET TMPDIR=src.tmp
SET ICON=wordmobi.svg
SET ZIP="C:\Arquivos de programas\7-Zip\7z.exe"

IF NOT EXIST %TMPDIR% mkdir %TMPDIR%

copy  %SRCDIR%\*.py  %TMPDIR%

%PYTHON% ensymble.py py2sis --verbose --uid=0xefefefef --version="%1" --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%ICON%" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%1.sis"

%ZIP% a -tzip %APPNAME%-%1-src.zip src\*.py


goto end

:error
echo Sintaxe: %0 version

:end

