REM 
REM DO NOT TRY TO GENERATE THE SIS FILE IF YOUR PATH CONTAINS SPACES.
REM ENSYMBLE DOES NOT SUPPORT THEM ! COPY THIS PROJECT TO C:\
REM BEFORE RUNNING THIS SCRIPT.
REM
@echo off

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET WMTMPDIR=src.tmp
SET ICON=wordmobi.svg  

REM put you zip tool here
SET ZIP="C:\Program Files (x86)\7-Zip\7z.exe"
REM Path to module-repo, inside Python For S60 
SET PYS60DIR=C:\Program Files (x86)\PythonForS60

SET OPTS=--verbose  --version="%1" --uid=0xefefefef ^
--appname="%APPNAME%" --icon="%ICON%" ^
--extrasdir=extras --heapsize=4k,5M --caps=%CAPBLS%

echo "Populating temp dir"
if exist "%WMTMPDIR%" rmdir /s /q "%WMTMPDIR%"
mkdir %WMTMPDIR%\extras\data\python\wordmobidir\loc
mkdir %WMTMPDIR%\extras\data\python\wordmobidir\res
copy  %SRCDIR%\*.py  %WMTMPDIR%\extras\data\python\wordmobidir
copy  %SRCDIR%\loc\*.py  %WMTMPDIR%\extras\data\python\wordmobidir\loc
copy  %SRCDIR%\res\*.png  %WMTMPDIR%\extras\data\python\wordmobidir\res
copy  %SRCDIR%\wordmobi.mif  %WMTMPDIR%\extras\data\python\wordmobidir
move %WMTMPDIR%\extras\data\python\wordmobidir\default.py  %WMTMPDIR%\
              
if not exist .\module-repo\ xcopy /E "%PYS60DIR%\module-repo" .\module-repo\
if not exist .\templates\   xcopy /E "%PYS60DIR%\templates"   .\templates\
if not exist ensymble.py    xcopy /E "%PYS60DIR%\ensymble.py" .
if not exist openssl.exe    xcopy /E "%PYS60DIR%\openssl.exe" .

echo "Copying extensions"
xcopy /E/Y extensions\* .\module-repo\dev-modules\

echo "Generating for Python 1.9.x"
%PYTHON% ensymble.py py2sis %OPTS% "%WMTMPDIR%" "%APPNAME%-%1.sis"

echo "Zipping source files"
%ZIP% a -r -tzip %APPNAME%-%1-src.zip src

goto end

:error
echo Sintaxe: %0 version

:end



