@echo off

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET WMTMPDIR=src.tmp
SET ICON=wordmobi.svg
REM put you zip tool here
SET ZIP="C:\Arquivos de programas\7-Zip\7z.exe"
REM Path to module-repo, inside Python For S60 
SET PYS60DIR=C:\Arquivos de programas\PythonForS60

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
  
echo "Copying project to PyS60 dir"
if exist "%PYS60DIR%\%WMTMPDIR%" rmdir /s/q "%PYS60DIR%\%WMTMPDIR%"
xcopy /E "%WMTMPDIR%" "%PYS60DIR%\%WMTMPDIR%\"
if exist "%PYS60DIR%\%ICON%" del /s/q "%PYS60DIR%\%ICON%"
copy "%ICON%" "%PYS60DIR%\%ICON%"

echo "Generating for Python 1.9.x"
pushd .
cd "%PYS60DIR%"
echo "Creating sis"
%PYTHON% ensymble.py py2sis %OPTS% "%WMTMPDIR%" "%APPNAME%-%1.sis"

popd
copy "%PYS60DIR%\%APPNAME%-%1.sis" .
echo "Zipping source files"
%ZIP% a -r -tzip %APPNAME%-%1-src.zip src\*.py src\*.mif src\*.png

echo "Erasing"
rmdir /s/q "%PYS60DIR%\%WMTMPDIR%"
del /s/q "%PYS60DIR%\%ICON%"
del "%PYS60DIR%\%APPNAME%-%1.sis"
rmdir /s/q "%WMTMPDIR%"

goto end

:error
echo Sintaxe: %0 version

:end


