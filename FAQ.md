# FAQ #

## Debug ##

### 0) XML-RPC are disabled on this blog ###

![http://wordmobi.googlecode.com/files/xmlrpc_disabled.png](http://wordmobi.googlecode.com/files/xmlrpc_disabled.png)

[Enable xml-rpc](http://www.wpnotifier.com/enable_xmlrpc.php) in your blog. Use the address http://blogname_address/wp-admin/options-writing.php. Follow [this instructions](http://www.wpnotifier.com/enable_xmlrpc.php).


### 1) Wordmobi is not running, unexpectedly closing or got stuck in some point ###

The best thing to do in such situation is running the scripts. Download the source code for your version e run wormobi from scripts. The download may be done [using subversion](http://code.google.com/p/wordmobi/source/checkout) or file by file, using the [source code browser](http://code.google.com/p/wordmobi/source/browse/#svn/trunk/wordmobi/src).

Afterward, do the following:

  1. Install python and python shell, version 1.4.5
  1. In our memory card, create directories e:\python and e:\python\lib
  1. Remove or comment the line at the end of window.py with the folowwing text: "app.set\_exit()". For commenting, just put # at the beginning, like #app.set\_exit().
  1. Copy all files into e:\python\lib, except default.py
  1. Copy default.py into e:\python\
  1. Run default.py via python shell, opening Python and selecting "Option->Run script"

This way, it will be possible to see the error messages or to add logs and alerts during execution. Please, collect these log messages and send them to developers.

### 2) After removing wordmobi, e:\wordmobi is not removed ###

Yes, the uninstall program can not remove e:\wordmobi. Please, remove it using your file manager. O just keep it if you want to install wordmobi again.