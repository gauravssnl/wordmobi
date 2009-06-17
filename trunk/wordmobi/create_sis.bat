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
SET PYS60DIR=D:\S60\python1_9_5

SET OPTS=--verbose --uid=0xefefefef --version="%1" ^
         --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%ICON%" ^
         --extrasdir=extras --heapsize=4k,5M --caps="%CAPBLS%"
     
echo "Generating for Python 1.9.5"
echo "Copying default modules"
if not exist .\module-repo\ xcopy /E "%PYS60DIR%\module-repo" .\module-repo\
if not exist .\templates\   xcopy /E "%PYS60DIR%\templates"   .\templates\

echo "populating temp dir"
rmdir /s /q %TMPDIR%
mkdir %TMPDIR%\extras\data\python\wordmobidir\loc
copy  %SRCDIR%\*.py  %TMPDIR%\extras\data\python\wordmobidir
copy  %SRCDIR%\loc\*.py  %TMPDIR%\extras\data\python\wordmobidir\loc
copy  %SRCDIR%\wordmobi.mif  %TMPDIR%\extras\data\python\wordmobidir
move %TMPDIR%\extras\data\python\wordmobidir\default.py  %TMPDIR%\

%PYTHON% ensymble.py py2sis %OPTS% "%TMPDIR%" "%APPNAME%-%1-py195.sis"

%ZIP% a -r -tzip %APPNAME%-%1-src.zip src\*.py src\*.mif

goto end

:error
echo Sintaxe: %0 version

:end

