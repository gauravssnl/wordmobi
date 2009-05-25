@echo off

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TXTFILE=README
SET TMPDIR=src.tmp
SET ICON=wordmobi.svg
REM put you zip tool here
SET ZIP="C:\Arquivos de programas\7-Zip\7z.exe"
REM Path to module-repo, inside Python For S60 
SET PYS60DIR=D:\S60\python1.9.4


SET OPTS=--verbose --uid=0xefefefef --version="%1" ^
         --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%ICON%" ^
         --caps="%CAPBLS%" "%TMPDIR%"
     
echo "Generating for Python 1.4.5..."
rmdir /s /q %TMPDIR%
mkdir %TMPDIR%
copy  %SRCDIR%\*.py  %TMPDIR%

%PYTHON% ensymble.py py2sis %OPTS% --heapsize=4k,2M "%APPNAME%-%1.sis"

echo "Generating for Python 1.9.4..."
rmdir /s /q %TMPDIR%
mkdir %TMPDIR%\extras\data\python
copy  %SRCDIR%\*.py  %TMPDIR%\extras\data\python
move %TMPDIR%\extras\data\python\default.py  %TMPDIR%\
if not exist .\module-repo\ xcopy /E "%PYS60DIR%\module-repo" .\module-repo\
if not exist .\templates\   xcopy /E "%PYS60DIR%\templates"   .\templates\

%PYTHON% ensymble_py19.py py2sis %OPTS% --extrasdir=extras --heapsize=4k,5M "%APPNAME%-%1-py19.sis"

%ZIP% a -tzip %APPNAME%-%1-src.zip src\*.py

goto end

:error
echo Sintaxe: %0 version

:end

