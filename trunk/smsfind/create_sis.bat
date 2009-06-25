@echo off

SET VERSION=1.0.0
SET PYTHON=C:\Python25\python
SET APPNAME=SMSearch
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET PYS60DIR=D:\S60\python1_9_5

if not exist .\module-repo\ xcopy /E "%PYS60DIR%\module-repo" .\module-repo\
if not exist .\templates\   xcopy /E "%PYS60DIR%\templates"   .\templates\

mkdir .\smsearch_sis\root\data\python\smsearch
copy  .\src\*.py   .\smsearch_sis\root\data\python\smsearch
move  .\smsearch_sis\root\data\python\smsearch\default.py   .\smsearch_sis

%PYTHON% .\ensymble.py py2sis --version="%VERSION%" --heapsize=4k,5M ^
          --appname="%APPNAME%" --caps="%CAPBLS%" --icon=smsearch.svg ^
          --extrasdir=root smsearch_sis "%APPNAME%%VERSION%.sis"
