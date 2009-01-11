import zlib
from icons import ICONS

fo = open('wordmobi2.mif','wb')

data = "".join(ICONS.split("\n"))
data = [ "%c" % chr(int(data[p:p+2],16)) for p in range(0,len(data),2) ]
data = "".join(data)
fo.write( zlib.decompress(data) )
fo.close()

