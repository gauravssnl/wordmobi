import e32
import sys
import os

# looking for install dir   
DEFDIR = u""
for d in e32.drive_list():
    appd = d + u"\\data\\python\\smsearch\\"
    if os.path.exists(appd + u"smsearch.py"):
        DEFDIR = appd
        break

if DEFDIR:
    sys.path.append(appd)
    from smsearch import SMSearch
    SMSearch().run()
