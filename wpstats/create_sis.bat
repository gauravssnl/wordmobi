@echo off

SET VERSION=1.0.2
SET PYTHON=C:\Python25\python
SET APPNAME=WPStats
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET PYS60DIR=D:\S60\python1_9_5

if not exist .\module-repo\ xcopy /E "%PYS60DIR%\module-repo" .\module-repo\
if not exist .\templates\   xcopy /E "%PYS60DIR%\templates"   .\templates\

mkdir .\wpstats_sis\root\data\python\wpstats\res
copy  .\src\*.py   .\wpstats_sis\root\data\python\wpstats
move  .\wpstats_sis\root\data\python\wpstats\default.py   .\wpstats_sis
copy  .\img\*.png   .\wpstats_sis\root\data\python\wpstats\res

%PYTHON% .\ensymble.py py2sis --version="%VERSION%" --heapsize=4k,5M ^
          --appname="%APPNAME%" --caps="%CAPBLS%" ^
          --extrasdir=root wpstats_sis "%APPNAME%%VERSION%.sis"
