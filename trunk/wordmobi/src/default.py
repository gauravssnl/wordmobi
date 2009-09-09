import e32
import sys
import os

# looking for install dir   
DEFDIR = u""
for d in e32.drive_list():
    appd = os.path.join(d,u"\\data\\python\\wordmobidir\\")
    if os.path.exists(os.path.join(appd,u"wordmobi.py")):
        DEFDIR = appd
        break

if DEFDIR:
    # fixing paths
    sys.path.append(DEFDIR)
    sys.path.append(os.path.join(DEFDIR,u"loc"))
    
    # pre compile all .py files to speedup next startups
    #if not os.path.exists(os.path.join(DEFDIR,u"wordmobi.pyc")):
    #    import py_compile
    #    [ py_compile.compile(os.path.join(DEFDIR,pf))
    #      for pf in os.listdir(DEFDIR)
    #      if pf.endswith('.py') ]
    #    [ py_compile.compile(os.path.join(DEFDIR,u"loc",pf))
    #      for pf in os.listdir(os.path.join(DEFDIR,u"loc"))
    #      if pf.endswith('.py') ]
    
    # starting wordmobi
    import wordmobi
    wordmobi.WordMobi().run()
else:
    import appuifw
    appuifw.note(u"Could not start Wordmobi","error")    
