import e32
import sys
import os

# looking for install dir   
DEFDIR = u""
for d in e32.drive_list():
    appd = d + u"\\data\\python\\wordmobidir\\"
    if os.path.exists(appd + u"wordmobi.py"):
        DEFDIR = appd
        break

if DEFDIR:
    # running wordmobi
    sys.path.append(DEFDIR)
    sys.path.append(os.path.join(DEFDIR,u"loc"))    
    import wordmobi
    wordmobi.WordMobi().run()
