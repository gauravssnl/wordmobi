import zlib

fi = open('wordmobi.mif','rb')
fo = open('icons.py','wt')

fo.write( "ICONS = '''")
data = zlib.compress(fi.read())
for p in range(0,len(data),40):
    line = data[p:p+40]
    fo.write( "\n" )
    d = "".join([ "%02X" % ord(b) for b in line ])
    fo.write( d )

fo.write( "'''\n")
fo.close()
fi.close()
