@echo on

IF "%1" EQU "" GOTO error

SET PYTHON=C:\Python25\python
SET APPNAME=wordmobi
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData
SET SRCDIR=src
SET TXTFILE=wordmobi_inst.txt
SET TMPDIR=src.tmp

SET PYFILES=viewcomments.py wmutil.py newpost.py settings.py persist.py editpost.py filesel.py viewpost.py wordmobi.py wordpresslib.py dt.py xmllib.py xmlrpclib.py

ECHO %TMPDIR%
IF NOT EXIST %TMPDIR% mkdir %TMPDIR%

for %%f in (%PYFILES%) do copy  %SRCDIR%\%%f  %TMPDIR%

copy %SRCDIR%\wordmobi.py %TMPDIR%\default.py

%PYTHON% .\ensymble.py py2sis --uid=0xefefefef --version="%1" --appname="%APPNAME%" --textfile="%TXTFILE%" --icon="%APPNAME%.svg" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%1.sis"

goto end

:error
echo "Sintaxe: " $0 " version"

:end

