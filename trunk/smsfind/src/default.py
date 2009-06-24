import e32
import sys
import os

# looking for install dir   
DEFDIR = u""
for d in e32.drive_list():
    appd = d + u"\\data\\python\\smsfind\\"
    if os.path.exists(appd + u"smsfind.py"):
        DEFDIR = appd
        break

if DEFDIR:
    sys.path.append(appd)
    from smsfind import SMSFind
    SMSFind().run()
